# Copyright (C) <2022>  <Zheng-Zhi Sun>
# This file is part of QuantumIntelligence. QuantumIntelligence 
# is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. 
# QuantumIntelligence is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details. You should have received a 
# copy of the GNU General Public License along with QuantumIntelligence. 
# If not, see <https://www.gnu.org/licenses/>.
import cirq
import cirq_web
import qiskit
import numpy as np
import torch as tc
import stim
import copy
import pyzx as zx
from QuantumIntelligence.QuantumSimulator import Gate
from QuantumIntelligence.BasicFunSZZ import tensor_trick as tt
from cirq.contrib.qasm_import import circuit_from_qasm
from cirq.circuits.qasm_output import QasmUGate
from qiskit.quantum_info import Operator



# [1, 0] is |0>, [0, 1] is |1>
# do not use fake functions, it will be removed soon
# please apply gate on position as list(range(?)) as much as possible, this will make it faster
# please control gate on position as list(range(?, n_qubit)) as much as possible, this will make it faster

class Circuit:

    def __init__(self, n_qubit, device='cpu', dtype=tc.complex64, hardware_size=None, qubit_position=None, index_layout=None):
        self.n_qubit = n_qubit
        self.device = device
        self.dtype = dtype
        self.gate_list = list()
        self.position_list = list()
        self.control_list = list()
        self.barrier_index = list()
        if hardware_size is None:
            # i think it will be a long time before we build a quantum computer with over 10^200 qubits
            self.hardware_size = (1, int(1e200))
        else:
            self.hardware_size = hardware_size
        if qubit_position is None:
            self.qubit_position = list()
            for ii in range(n_qubit):
                self.qubit_position.append((ii // self.hardware_size[1], ii % self.hardware_size[1]))
        else:
            if index_layout is None:
                self.qubit_position = qubit_position
            else:
                self.qubit_position = list()
                assert len(index_layout) == n_qubit
                for ii in range(n_qubit):
                    # self.qubit_position.append(qubit_position[index_layout.index(ii)])
                    self.qubit_position.append(qubit_position[index_layout[ii]])


    @property
    def requires_grad(self):
        flag = list()
        for gg in self.gate_list:
            flag.append(gg.requires_grad)
        return flag

    @requires_grad.setter
    def requires_grad(self, requires_grad):
        if isinstance(requires_grad, bool):
            for gg in self:
                gg.requires_grad = requires_grad
        else:
            for nn in range(len(self)):
                self.gate_list[nn].requires_grad = requires_grad[nn]

    # core functions start

    def compose(self, circuit, position=None, control=None, inverse=False):
        if isinstance(circuit, Circuit):
            tmp_circuit = copy.deepcopy(circuit)
            if inverse:
                tmp_circuit.inv()
            self.__extend(tmp_circuit, position=position, control=control)
        elif isinstance(circuit, Gate.Gate):
            if position is None:
                raise ValueError('position is needed when compose gate')
            self.add_single_gate(gate=circuit, position=position, control=control, inverse=inverse)
        else:
            raise ValueError('input is not Gate or Circuit')

    def __extend(self, circuit, position=None, control=None):
        if not isinstance(circuit, Circuit):
            raise TypeError('this function is used to extend circuit. Use append or compose to add single gate')
        if control is None:
            control = []
        if position is None:
            position = list(range(self.n_qubit))
        assert len(position) == circuit.n_qubit
        for ii in range(len(circuit)):
            cc = circuit[ii]
            new_p = list()
            new_c = list()
            for oo in cc[1]:
                new_p.append(position[oo])
            for oo in cc[2]:
                new_c.append(position[oo])
            for oo in control:
                new_c.append(oo)
            self.append(gate=cc[0], position=new_p.copy(), control=new_c.copy())

    def add_single_gate(self, gate:Gate, position, control=None, inverse=False):
        # gate can be sparse, but there seems to be no speedup
        # one should be careful when add inverse gates
        # the gate will be cloned and detached by default

        # do not change the following code, or some bugs would occur in circuit.ch
        gate = Gate.Gate(gate, independent=True)
        # gate = Gate.Gate(gate, independent=True).to(self.device).to(self.dtype)

        if tt.have_same_iterable(position, control):
            raise ValueError('position and control have same qubits')
        self.position_list.append(position)
        if control is None:
            control = []
        self.control_list.append(control)
        if inverse:
            gate.inv()
        self.gate_list.append(gate)

    def append(self, gate, position, control=None, inverse=False):
        # this is just another name of add single gate
        self.add_single_gate(gate, position=position, control=control, inverse=inverse)

    def repeat_append(self, gate, position_list, inverse=False):
        for position in position_list:
            self.add_single_gate(gate, position=position, inverse=inverse)

    def inv(self):
        self.gate_list.reverse()
        self.position_list.reverse()
        self.control_list.reverse()
        for gate in self.gate_list:
            gate.inv()

    def return_inv(self):
        tmp_circuit = copy.deepcopy(self)
        tmp_circuit.gate_list.reverse()
        tmp_circuit.position_list.reverse()
        tmp_circuit.control_list.reverse()
        for gate in tmp_circuit.gate_list:
            gate.inv()
        return tmp_circuit

    def to(self, device_or_dtype):
        for cc in self.gate_list:
            cc.to(device_or_dtype)
        return self

    def square(self):
        for gate in self.gate_list:
            gate.square()

    def regularize_position(self, index):

        self.position_list[index] = list(map(lambda x: x % self.n_qubit, self.position_list[index]))
        self.control_list[index] = list(map(lambda x: x % self.n_qubit, self.control_list[index]))

    def regularize_all_position(self):
        for ii in range(len(self)):
            self.regularize_position(ii)

    def __getitem__(self, index):
        return self.gate_list[index], self.position_list[index], self.control_list[index]

    def __len__(self):
        return len(self.gate_list)

    def __add__(self, circuit):

        if circuit.n_qubit != self.n_qubit:
            raise ValueError('error in +, n_qubit not equal')

        tmp_circuit = Circuit(self.n_qubit, device=self.device, dtype=self.dtype, qubit_position=self.qubit_position)
        tmp_circuit.gate_list = self.gate_list + circuit.gate_list
        tmp_circuit.position_list = self.position_list + circuit.position_list
        tmp_circuit.control_list = self.control_list + circuit.control_list
        return tmp_circuit

    def __copy__(self):
        raise NameError('I do not permit copy for now. Please use deepcopy().')

    def pop(self, index):
        self.gate_list.pop(index)
        self.position_list.pop(index)
        self.control_list.pop(index)

    def clear(self):
        while len(self) > 0:
            self.pop(0)


    def add_noise_gate(self, strength=0.01):
        old_circuit = copy.deepcopy(self)
        self.clear()
        for ii in range(len(old_circuit)):
            self.append(old_circuit.gate_list[ii], old_circuit.position_list[ii], old_circuit.control_list[ii])
            combined_position = old_circuit.position_list[ii] + old_circuit.control_list[ii]
            if len(combined_position) > 0:
                for pp in combined_position:
                    tmp_noise = Gate.noise_gate_single_gaussian(strength=strength, device=self.device, dtype=self.dtype)
                    self.append(gate=tmp_noise, position=[pp])

    def cal_barrier(self):
        # raise ValueError('This function is temporarily unavailable')
        self.regularize_all_position()
        position_list = list(range(self.n_qubit))
        flag = False
        for ii in range(len(self)):
            print(ii, self.position_list[ii], self.control_list[ii])
            for nn in self.position_list[ii]:
                if nn not in position_list:
                    flag = True
            for nn in self.control_list[ii]:
                if nn not in position_list:
                    flag = True

            if flag:
                self.barrier_index.append(ii)
                position_list = list(range(self.n_qubit))
                flag = False
            for nn in self.position_list[ii]:
                position_list.remove(nn)
            for nn in self.control_list[ii]:
                position_list.remove(nn)

    def barrier(self):
        self.barrier_index.append(len(self)-1)


    def regularize_gates(self):
        new_gate_list = []
        new_position_list = []
        new_control_list = []
        while len(self) > 0:
            index_list_strict = list(range(self.n_qubit))
            index_list_loose = list(range(self.n_qubit))
            ii = 0
            while ii < len(self):

                flag = True
                for nn in self.position_list[ii]:
                    if nn not in index_list_strict:
                        flag = False
                for nn in self.control_list[ii]:
                    if nn not in index_list_loose:
                        flag = False

                if flag:
                    for nn in self.position_list[ii]:
                        if nn in index_list_strict:
                            index_list_strict.remove(nn)
                        if nn in index_list_loose:
                            index_list_loose.remove(nn)
                    for nn in self.control_list[ii]:
                        if nn in index_list_strict:
                            index_list_strict.remove(nn)
                        if nn in index_list_loose:
                            index_list_loose.remove(nn)
                    new_gate_list.append(self.gate_list[ii])
                    new_position_list.append(self.position_list[ii])
                    new_control_list.append(self.control_list[ii])
                    self.pop(ii)
                else:
                    for nn in self.position_list[ii]:
                        if nn in index_list_strict:
                            index_list_strict.remove(nn)
                        if nn in index_list_loose:
                            index_list_loose.remove(nn)
                    for nn in self.control_list[ii]:
                        if nn in index_list_strict:
                            index_list_strict.remove(nn)
                    ii = ii + 1
        self.gate_list = new_gate_list
        self.position_list = new_position_list
        self.control_list = new_control_list

    def map_qubits(self, qubit_map:dict):
        for ii in range(len(self)):
            self.position_list[ii] = [qubit_map[pp] for pp in self.position_list[ii]]
            self.control_list[ii] = [qubit_map[pp] for pp in self.control_list[ii]]
        self.qubit_position = [self.qubit_position[ii] for ii in qubit_map.keys()]
        self.n_qubit = len(qubit_map.keys())

    def using_qubits(self):
        using_qubits = list()
        for _, position, control in self:
            using_qubits.extend(position)
            using_qubits.extend(control)
        using_qubits = sorted(list(set(using_qubits)))
        return using_qubits

    def map2usingQubits(self):
        using_qubits = self.using_qubits()
        map_dict = dict(zip(using_qubits, range(len(using_qubits))))
        self.map_qubits(map_dict)
        self.n_qubit = len(using_qubits)

    # core functions end
    # practical functions start

    # universal gate set from experiment

    def rx_gate(self, position, theta=np.pi, control=None):
        tmp_gate = Gate.rx_gate(theta=theta)
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def ry_gate(self, position, theta=np.pi, control=None):
        tmp_gate = Gate.ry_gate(theta=theta)
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def rz_gate(self, position, theta=np.pi, control=None):
        tmp_gate = Gate.rz_gate(theta=theta)
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def cz_gate(self, position):
        tmp_gate = Gate.cz_gate()
        self.add_single_gate(tmp_gate, position=position)

    # decompose circuit to experimental gates

    def decompose2experimental_gate(self):
        # global phases are ignored

        old_gate_list = self.gate_list
        old_position_list = self.position_list
        old_control_list = self.control_list

        self.gate_list = list()
        self.position_list = list()
        self.control_list = list()

        experimental_gate_set = ['RX', 'RY', 'RZ', 'CZ']
        supported_label = ['X', 'Y', 'Z', 'H']
        for ii in range(len(old_gate_list)):
            tmp_label = old_gate_list[ii].label
            if isinstance(tmp_label, tuple):
                tmp_label = tmp_label[0]
            tmp_position = old_position_list[ii]
            tmp_control = old_control_list[ii]

            if tmp_label is None:
                raise ValueError('The ', str(ii), '-th gate has no label')
            if len(tmp_control) > 1:
                raise ValueError('Do not support multi controlled ', tmp_label)

            if tmp_label in experimental_gate_set:
                if len(tmp_control) == 0:
                    self.append(old_gate_list[ii], position=tmp_position)
                elif len(tmp_control) == 1:
                    raise ValueError('Waiting to support controlled ', tmp_label)
            elif tmp_label in supported_label:
                if tmp_label == 'Z':
                    if len(tmp_control) == 0:
                        self.rz_gate(position=tmp_position, theta=np.pi)
                    elif len(tmp_control) == 1:
                        self.cz_gate(position=[tmp_position+tmp_control])
                elif tmp_label == 'X':
                    if len(tmp_control) == 0:
                        self.rx_gate(position=tmp_position, theta=np.pi)
                    elif len(tmp_control) == 1:
                        self.rz_gate(position=tmp_position, theta=np.pi)
                        self.ry_gate(position=tmp_position, theta=np.pi/2)
                        self.cz_gate(position=[tmp_position+tmp_control])
                        self.ry_gate(position=tmp_position, theta=-np.pi / 2)
                        self.rz_gate(position=tmp_position, theta=-np.pi)
                elif tmp_label == 'Y':
                    if len(tmp_control) == 0:
                        self.ry_gate(position=tmp_position, theta=np.pi)
                    elif len(tmp_control) == 1:
                        self.rz_gate(position=tmp_position, theta=-np.pi/2)
                        self.ry_gate(position=tmp_position, theta=-np.pi/2)
                        self.cz_gate(position=[tmp_position+tmp_control])
                        self.ry_gate(position=tmp_position, theta=np.pi/2)
                        self.rz_gate(position=tmp_position, theta=np.pi/2)
                elif tmp_label == 'H':
                    if len(tmp_control) > 1:
                        raise ValueError('Do not support controlled ', tmp_label)
                    self.rz_gate(position=tmp_position, theta=np.pi)
                    self.ry_gate(position=tmp_position, theta=np.pi/2)
                else:
                    raise ValueError('tired')
            else:
                raise ValueError('The unsupported label is', tmp_label)

    def cancel_rz_clifford_exp(self):
        rz_index = len(self) - 1
        while rz_index >=0:
            if self.gate_list[rz_index].label[0] == 'RZ':
                walk_index = rz_index
                walk_label = self.gate_list[walk_index].label
                walk_position = self.position_list[walk_index][0]
                self.pop(walk_index)
                while walk_index > 0:
                    check_index = walk_index - 1
                    if  walk_position in self.position_list[check_index]:
                        check_label = self.gate_list[check_index].label
                        if check_label == 'CZ':
                            pass
                        elif check_label[0] == 'RZ':
                            new_theta = walk_label[1] + check_label[1]
                            new_theta = ((new_theta/np.pi) % 2) * np.pi
                            walk_label = ('RZ', new_theta)
                            self.pop(check_index)
                            walk_index = walk_index - 1
                            rz_index = rz_index - 1
                            if ((new_theta/np.pi) % 2) == 0:
                                walk_index = -1
                        elif check_label[0] =='RX':
                            if np.isclose((walk_label[1]/np.pi) % 2, 0.5):
                                self.gate_list[check_index] = Gate.ry_gate(theta=check_label[1])
                            elif np.isclose((walk_label[1]/np.pi) % 2, 1):
                                self.gate_list[check_index] = Gate.rx_gate(theta=-check_label[1])
                            elif np.isclose((walk_label[1]/np.pi) % 2, 1.5):
                                self.gate_list[check_index] = Gate.ry_gate(theta=-check_label[1])
                            else:
                                raise ValueError('tired', 'walk_label[1]/np.pi is', walk_label[1]/np.pi)
                        elif check_label[0] =='RY':
                            if (walk_label[1]/np.pi) % 2 == 0.5:
                                self.gate_list[check_index] = Gate.rx_gate(theta=-check_label[1])
                            elif (walk_label[1]/np.pi) % 2 == 1:
                                self.gate_list[check_index] = Gate.ry_gate(theta=-check_label[1])
                            elif (walk_label[1]/np.pi) % 2 == 1.5:
                                self.gate_list[check_index] = Gate.rx_gate(theta=check_label[1])
                            else:
                                raise ValueError('tired', 'walk_label[1]/np.pi is', walk_label[1]/np.pi)
                        else:
                            raise ValueError('tired')
                    walk_index = walk_index - 1
            rz_index = rz_index - 1
        self.to(self.device).to(self.dtype)

    def cancel_rxy_clifford_exp(self):
        rxy_index = len(self) - 1
        while rxy_index >0:
            if self.gate_list[rxy_index].label[0] in ('RX', 'RY'):
                walk_index = rxy_index
                walk_label = self.gate_list[walk_index].label
                walk_position = self.position_list[walk_index][0]
                if (walk_label[1]/np.pi) % 2 ==0:
                    walk_index = -1
                while walk_index > 0:
                    check_index = walk_index - 1
                    if  walk_position in self.position_list[check_index]:
                        check_label = self.gate_list[check_index].label
                        if check_label == 'CZ':
                            walk_index = 1
                        elif check_label[0] == 'RZ':
                            raise ValueError('cancel rz first')
                        elif check_label[0] == walk_label[0]:
                            new_theta = walk_label[1] + check_label[1]
                            new_theta = ((new_theta/np.pi) % 2) * np.pi
                            walk_label = (walk_label[0], new_theta)
                            self.pop(check_index)
                            rxy_index = rxy_index - 1
                            if ((new_theta/np.pi) % 2) == 0:
                                walk_index = -1
                        elif check_label[0] in ('RX', 'RY'):
                            if (check_label[1]/np.pi) % 2 == 0:
                                self.pop(check_index)
                                walk_index = walk_index - 1
                                rxy_index = rxy_index - 1
                            elif (check_label[1]/np.pi) % 2 == 1:
                                walk_label = (walk_label[0], -walk_label[1])
                            else:
                                if (walk_label[1]/np.pi) % 2 == 1:
                                    self.gate_list[check_index] = Gate.r_gate(theta=-check_label[1], label=check_label[0])
                                else:
                                    walk_index = 1
                        else:
                            raise ValueError('tired')
                    walk_index = walk_index - 1
                if walk_index <= 0:
                    self.pop(rxy_index)
                if walk_index  == 0:
                    self.gate_list.insert(check_index + 1, Gate.r_gate(theta=walk_label[1], label=walk_label[0]))
                    self.position_list.insert(check_index + 1, [walk_position])
                    self.control_list.insert(check_index + 1, [])
            rxy_index = rxy_index - 1
        self.to(self.device).to(self.dtype)
            
    def cancel_xyz_surface_code_abandoned(self):
        walk_index = 0
        xyz_list = ['X', 'Y', 'Z']
        rxyz_list = ['RX', 'RY', 'RZ']
        while walk_index < len(self):
            pop_flag = False
            tmp_label = self.gate_list[walk_index].label
            tmp_control = self.control_list[walk_index]
            if tmp_label in xyz_list:
                if len(tmp_control) == 0:
                    pop_flag = True
            elif tmp_label[0] in rxyz_list:
                if len(tmp_control) == 0:
                    if (tmp_label[1]/np.pi) % 1 == 0:
                        pop_flag = True

            if pop_flag:
                self.pop(walk_index)
            else:
                walk_index = walk_index + 1
        self.to(self.device).to(self.dtype)


    # useful gates and circuits

    def labelled_gate(self, name, position, control=None, params=None):
        tmp_gate = Gate.labelled_simple_gate(name=name, params=params)
        for pp in position:
            if not isinstance(pp, list):
                pp = [pp]
            self.add_single_gate(tmp_gate, position=pp, control=control)


    def x_gate(self, position, control=None):
        tmp_gate = Gate.x_gate()
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def y_gate(self, position, control=None):
        tmp_gate = Gate.y_gate()
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def z_gate(self, position, control=None):
        tmp_gate = Gate.z_gate()
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def hadamard(self, position, control=None):
        tmp_gate = Gate.hadamard()
        for pp in position:
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def phase_shift(self, position, theta=tc.pi, control=None):
        for pp in position:
            tmp_gate = Gate.phase_shift(theta)
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def not_gate(self, position, control=None):
        for pp in position:
            tmp_gate = Gate.not_gate()
            self.add_single_gate(tmp_gate, position=[pp], control=control)

    def rand_gate(self, dim, position, control=None, requires_grad=False):
        tmp_gate = Gate.rand_gate(dim, device=self.device, dtype=self.dtype, requires_grad=requires_grad)
        self.add_single_gate(tmp_gate, position=position, control=control)

    def swap_gate(self, position, control=None):
        if len(position) != 2:
            raise ValueError('wrong use')
        else:
            tmp_gate = Gate.swap_gate()
            self.add_single_gate(tmp_gate, position=position, control=control)

    def ccx_gate(self, position, control=None):
        tmp_gate = Gate.ccx_gate()
        self.add_single_gate(tmp_gate, position=position, control=control)

    def time_evolution(self, hamiltonian, time, position, control=None):
        tmp_gate = Gate.time_evolution(hamiltonian, time, device=self.device, dtype=self.dtype)
        self.add_single_gate(tmp_gate, position=position, control=control)

    def qft(self, position, control=None, inverse=False, ordering=True):
        if control is None:
            control = []
        tmp_circuit = qft(self.n_qubit, position=position, control=control, inverse=inverse, ordering=ordering,
                          device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)
        
    def adder(self, p_add_1, p_add_2, control=None, inverse=False):
        if control is None:
            control = []
        tmp_circuit = adder(n_qubit=self.n_qubit, p_add_1=p_add_1, p_add_2=p_add_2, control=control, inverse=inverse,
                            device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def subtractor(self, p_add_1, p_add_2, control=None, inverse=False):
        if control is None:
            control = []
        tmp_circuit = subtractor(n_qubit=self.n_qubit, p_add_1=p_add_1, p_add_2=p_add_2, control=control, inverse=inverse,
                            device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)
        
    def multiplicator(self, p_mul_1, p_mul_2, p_result, control=None, inverse=False):
        if control is None:
            control = []
        tmp_circuit = multiplicator(n_qubit=self.n_qubit, p_mul_1=p_mul_1, p_mul_2=p_mul_2, p_result=p_result,
                                    control=control, inverse=inverse,device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def ch(self, unitary, position_phi, position_c, control=None, inverse=False):
        tmp_circuit = ch(self.n_qubit, unitary, position_phi, position_c, control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def qpe(self, unitary, position_phi, position_qpe, control=None, inverse=False):
        tmp_circuit = qpe(self.n_qubit, unitary, position_phi, position_qpe, control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def add_one(self, position=None, control=None, inverse=False):
        tmp_circuit = add_one(self.n_qubit, position, control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def qhc(self, unitary, position_phi, position_qpe, position_f, n_f=None,
            control=None, inverse=False):
        tmp_circuit = qhc(self.n_qubit, unitary, position_phi, position_qpe, position_f,
                          n_f, control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def quantum_coin(self, unitary, position_phi, position_coin, control=None, inverse=False):
        tmp_circuit = quantum_coin(self.n_qubit, unitary, position_phi, position_coin,
                                   control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def qdc(self, unitary, position_phi, position_coin, position_f,
            n_f=None, control=None, inverse=False):
        tmp_circuit = qdc(self.n_qubit, unitary, position_phi, position_coin, position_f,
                          n_f, control, inverse, device=self.device, dtype=self.dtype)
        self.__extend(tmp_circuit)

    def to_qiskit(self):
        qiskit_circuit = qiskit.QuantumCircuit(self.n_qubit)
        supported_label = ('CZ', 'CX', 'CY', 'S', 'T', 'CCX', 'CH')
        supported_label_c = ('X', 'Y', 'Z', 'NOT', 'Phase', 'SWAP','CP', 'H')
        supported_label_r = ('RX', 'RY', 'RZ')
        supported_label_u = ('U3', 'U4')
        for ii in range(len(self)):
            old_label = self.gate_list[ii].label
            q_position = self.position_list[ii]
            c_position = self.control_list[ii]
            if old_label is None:
                # print('test code, gate has no label')
                unitary = qiskit.extensions.UnitaryGate(self.gate_list[ii].tensor.cpu().numpy())
                if len(c_position)>0:
                    unitary = unitary.control(len(c_position))
                qiskit_circuit.append(unitary, c_position + q_position)
            else:
                if old_label in supported_label:
                    if len(c_position) > 0:
                        raise ValueError('Do not support control.', supported_label)
                    # note the swap between control and target qubit
                    if old_label == 'CX':
                        qiskit_circuit.cx(control_qubit=q_position[0], target_qubit=q_position[1])
                    elif old_label == 'CY':
                        qiskit_circuit.cy(control_qubit=q_position[0], target_qubit=q_position[1])
                    elif old_label == 'CZ':
                        qiskit_circuit.cz(control_qubit=q_position[0], target_qubit=q_position[1])
                    elif old_label == 'CH':
                        qiskit_circuit.ch(control_qubit=q_position[0], target_qubit=q_position[1])
                    elif old_label == 'CCX':
                        qiskit_circuit.ccx(control_qubit1=q_position[0], control_qubit2=q_position[1],
                                           target_qubit=q_position[2])
                    elif old_label == 'S':
                        if self.gate_list[ii].inverse:
                            qiskit_circuit.sdg(qubit=q_position)
                        else:
                            qiskit_circuit.s(qubit=q_position)
                    elif old_label == 'T':
                        if self.gate_list[ii].inverse:
                            qiskit_circuit.tdg(qubit=q_position)
                        else:
                            qiskit_circuit.t(qubit=q_position)
                    else:
                        raise ValueError('Please report this bug to deveploper. Error occurs in supported_label.')
                elif old_label in supported_label_c or old_label[0] in supported_label_c:
                    if len(c_position) == 0:
                        if old_label in ('X', 'NOT'):
                            qiskit_circuit.x(qubit=q_position)
                        elif old_label == 'Y':
                            qiskit_circuit.y(qubit=q_position)
                        elif old_label == 'Z':
                            qiskit_circuit.z(qubit=q_position)
                        elif old_label == 'H':
                            qiskit_circuit.h(qubit=q_position)
                        elif old_label[0]=='CP':
                            theta = old_label[1]
                            if self.gate_list[ii].inverse:
                                theta = -theta
                            if len(c_position) == 0:
                                qiskit_circuit.cp(theta=theta, control_qubit=q_position[0], target_qubit=q_position[1])
                            else:
                                raise ValueError('Do not support control.', old_label)
                        elif old_label[0] in ['Phase', 'SWAP'] or old_label in ['Phase', 'SWAP']:
                            # the code of swap,  phase, and control phase circuit is in the following
                            pass
                        else:
                            print(old_label)
                            raise ValueError('Please report this bug to deveploper. Error occurs in supported_label_c.')
                    elif len(c_position) > 0:
                        # testing
                        if old_label in ('X', 'NOT'):
                            qiskit_circuit.mcx(control_qubits=c_position, target_qubit=q_position)
                        elif old_label == 'Z':
                            if len(c_position) == 1:
                                qiskit_circuit.cz(control_qubit=c_position, target_qubit=q_position)
                            elif len(c_position) == 2:
                                qiskit_circuit.ccz(control_qubits=c_position, target_qubit=q_position)
                            else:
                                raise ValueError('Do not support multi control.', supported_label_c)
                        elif old_label == 'H':
                            if len(c_position) == 1:
                                qiskit_circuit.ch(control_qubit=c_position, target_qubit=q_position)
                            else:
                                raise ValueError('Do not support multi control.', supported_label_c)
                    if old_label == 'SWAP':
                        if len(c_position) == 0:
                            qiskit_circuit.cx(control_qubit=q_position[0], target_qubit=q_position[1])
                            qiskit_circuit.cx(control_qubit=q_position[1], target_qubit=q_position[0])
                            qiskit_circuit.cx(control_qubit=q_position[0], target_qubit=q_position[1])
                        elif len(c_position) == 1:
                            qiskit_circuit.cswap(control_qubit=c_position, target_qubit1=q_position[0], target_qubit2=q_position[1])
                        else:
                            raise ValueError('Do not support multi control.', old_label)
                    if old_label[0]=='Phase':
                        theta = old_label[1]
                        if self.gate_list[ii].inverse:
                            theta = -theta
                        if len(c_position) == 0:
                            qiskit_circuit.p(theta=theta, qubit=q_position)
                        elif len(c_position) == 1:
                            qiskit_circuit.cp(theta=theta, control_qubit=c_position, target_qubit=q_position)
                        elif len(c_position) >= 2:
                            qiskit_circuit.mcp(lam=theta,control_qubits=c_position, target_qubit=q_position)
                        else:
                            raise ValueError('Do not support multi control.', old_label)
                elif old_label[0] in supported_label_r:
                    theta = old_label[1]
                    if self.gate_list[ii].inverse:
                        theta = -theta
                    if len(c_position) > 1:
                        raise ValueError('Do not support multi control.', supported_label_r)
                    elif len(c_position) == 0:
                        if old_label[0] == 'RX':
                            qiskit_circuit.rx(theta=theta, qubit=q_position)
                        elif old_label[0] == 'RY':
                            qiskit_circuit.ry(theta=theta, qubit=q_position)
                        elif old_label[0] == 'RZ':
                            qiskit_circuit.rz(phi=theta, qubit=q_position)
                        else:
                            raise ValueError('Please report this bug to deveploper. Error occurs in supported_label_r.')
                    elif len(c_position) == 1:
                        if old_label[0] == 'RX':
                            qiskit_circuit.crx(theta=theta, control_qubit=c_position, target_qubit=q_position)
                        elif old_label[0] == 'RY':
                            qiskit_circuit.cry(theta=theta, control_qubit=c_position, target_qubit=q_position)
                        elif old_label[0] == 'RZ':
                            qiskit_circuit.crz(phi=theta, control_qubit=c_position, target_qubit=q_position)
                        else:
                            raise ValueError('Please report this bug to deveploper. Error occurs in supported_label_r.')
                elif old_label[0] in supported_label_u:
                    theta = (old_label[1][0], old_label[1][1], old_label[1][2])
                    if self.gate_list[ii].inverse:
                        theta = (-theta[0], - theta[2], - theta[1])
                    if len(c_position) > 1:
                        raise ValueError('Do not support multi control.', supported_label_u)
                    elif len(c_position) == 0:
                        if old_label[0] in ('U3', 'U4'):
                            qiskit_circuit.u(theta[0], theta[1], theta[2], qubit=q_position)
                    elif len(c_position) == 1:
                        if old_label[0] in ('U3', 'U4'):
                            if old_label[0] == 'U4':
                                theta3 = old_label[1][3]
                            else:
                                theta3 = 0
                            if self.gate_list[ii].inverse:
                                theta3 = - theta3
                            qiskit_circuit.cu(*theta, gamma=theta3, control_qubit=c_position, target_qubit=q_position)
                        else:
                            raise ValueError('tired')
                else:
                    raise ValueError('Do not support the label of', str(ii), 'th gate, which is', old_label)
            if ii in self.barrier_index:
                qiskit_circuit.barrier()
        return qiskit_circuit


    def to_qasm(self):
        # this is achieved by qiskit
        qiskit_circuit = self.to_qiskit()
        qasm_circuit = qiskit_circuit.qasm()
        return qasm_circuit
    
    
    def to_tensor(self):
        qiskit_circuit = self.to_qiskit()
        out_tensor = Operator(qiskit_circuit.reverse_bits()).data
        out_tensor = tc.from_numpy(out_tensor).to(self.device).to(self.dtype)
        return out_tensor
        

    def from_qasm(self, qasm_circuit, replace=False, from_file=False):
        if from_file:
            qiskit_circuit = qiskit.QuantumCircuit.from_qasm_file(qasm_circuit)
        else:
            qiskit_circuit = qiskit.QuantumCircuit.from_qasm_str(qasm_circuit)
        circuit = self.from_qiskit(qiskit_circuit=qiskit_circuit, replace=replace)
        if not replace:
            return circuit

    def from_qiskit(self, qiskit_circuit, replace=False):
        assert self.n_qubit == qiskit_circuit.num_qubits
        qiskit_register = qiskit_circuit.qregs[0]
        if qiskit_circuit.layout is not None:
            index_layout = qiskit_circuit.layout.final_index_layout()
        else:
            index_layout = None
        circuit = Circuit(self.n_qubit, self.device, self.dtype, qubit_position=self.qubit_position,
                          hardware_size=self.hardware_size, index_layout=index_layout)
        supported_name_no_params = ['x', 'y', 'z', 'h', 'cx', 'cy', 'cz', 'ch', 'ccx', 'swap']
        supported_name_specific = ['sdg', 'tdg', 's', 't']
        supported_name_with_params = ['rx', 'ry', 'rz','cp']
        supported_name_with_complex_params = ['u3', 'u']
        for instruction in qiskit_circuit:
            operation = instruction.operation
            qubits = instruction.qubits
            name = operation.name
            position = []
            for qq in qubits:
                if index_layout is None:
                    position.append(qiskit_register.index(qq))
                else:
                    position.append(index_layout.index(qiskit_register.index(qq)))
            if len(position) > 1:
                position = [position]
            if name in supported_name_no_params:
                circuit.labelled_gate(name=name.upper(), position=position)
            elif name in supported_name_with_params:
                params = operation.params[0]
                if not isinstance(params, float):
                    params = float(params)
                circuit.labelled_gate(name=name.upper(), position=position, params=params)
            elif name in supported_name_specific:
                if name == 'sdg':
                    circuit.append(Gate.s_gate(), position=position, inverse=True)
                    # circuit.rz_gate(position=position, theta=-np.pi/2)
                elif name == 'tdg':
                    circuit.append(Gate.t_gate(), position=position, inverse=True)
                    # circuit.rz_gate(position=position, theta=-np.pi/4)
                elif name == 't':
                    circuit.append(Gate.t_gate(), position=position)
                    # circuit.rz_gate(position=position, theta=np.pi/4)
                elif name == 's':
                    circuit.append(Gate.s_gate(), position=position)
                    # circuit.rz_gate(position=position, theta=np.pi/2)
                else:
                    raise ValueError('Please report this bug to deveploper. Error occurs in supported_name_specific.')
            elif name in supported_name_with_complex_params:
                if name in ['u3', 'u']:
                    params = tuple(float(ii) for ii in operation.params)
                    circuit.append(Gate.u3(theta=params), position=position)
                else:
                    raise ValueError('Please report this bug to deveploper. Error occurs in supported_name_specific.')
            else:
                raise ValueError('Does not support', name)
        if replace:
            self.clear()
            self.qubit_position = circuit.qubit_position
            self.compose(circuit)
        else:
            return circuit

    def positive_theta(self):
        for ii in range(len(self)):
            old_label = self.gate_list[ii].label
            if old_label[0] in ('RX', 'RY', 'RZ'):
                while self.gate_list[ii].label[1] <= 0:
                    self.gate_list[ii].label = (old_label[0], self.gate_list[ii].label[1] + 4*np.pi)


    def zx_optimize(self, replace=False):
        self.positive_theta()
        qiskit_circuit = self.to_qiskit()
        zx_circuit = zx.Circuit.from_qasm(self.to_qasm())
        # print(zx_circuit)
        new_zx_circuit = zx.optimize.basic_optimization(zx_circuit.split_phase_gates(), do_swaps=False)
        # new_zx_circuit = zx_circuit
        new_qasm_circuit = new_zx_circuit.to_qasm()
        new_qiskit_circuit = qiskit.QuantumCircuit.from_qasm_str(new_qasm_circuit)
        new_qiskit_circuit = qiskit.transpile(new_qiskit_circuit,basis_gates=['cz', 'rx', 'rz'],optimization_level=3)
        circuit = self.from_qiskit(new_qiskit_circuit, replace=True)
        # circuit = self.from_qasm(new_qasm_circuit, replace=replace)
        if not replace:
            return circuit

    def qiskit_transpile(self, replace=True, **kwargs):
        qiskit_circuit = qiskit.transpile(self.to_qiskit(),**kwargs)
        circuit = self.from_qiskit(qiskit_circuit=qiskit_circuit, replace=replace)
        if not replace:
            return circuit

    def to_stim(self):
        stim_circuit = stim.Circuit()
        same_label_control0_list = ['CX', 'CY', 'CZ', 'H']
        dag_label_control0_list = ['S']
        same_label_control1_list = ['X', 'Y', 'Z']
        tuple_RD_list = ['RX', 'RY', 'RZ']

        for ii in range(len(self)):
            old_label = self.gate_list[ii].label

            if old_label is None:
                raise ValueError('The ', str(ii), '-th gate does not have label.')
            if old_label in same_label_control0_list:
                if len(self.control_list[ii]) > 0:
                    raise ValueError('Do not support control.')
                new_position = self.position_list[ii]
                new_label = old_label
            elif old_label in dag_label_control0_list:
                if len(self.control_list[ii]) > 0:
                    raise ValueError('Do not support control.')
                new_position = self.position_list[ii]
                new_label = old_label
                if self.gate_list[ii].inverse:
                    new_label = new_label + '_DAG'
            elif old_label in same_label_control1_list:
                tmp_control = self.control_list[ii]
                if len(tmp_control) == 0:
                    new_position = self.position_list[ii]
                    new_label = old_label
                elif len(tmp_control) == 1:
                    new_position = tmp_control + self.position_list[ii]
                    new_label = 'C' + old_label
                else:
                    raise ValueError('Do not support multi control.')
            elif old_label[0] in tuple_RD_list:
                if len(self.control_list[ii]) > 0:
                    raise ValueError('Do not support control for RD gate.')
                new_label = old_label[0][1]
                if self.gate_list[ii].inverse:
                    old_label = (old_label[0], -old_label[1])
                while old_label[1]/np.pi > 1:
                    old_label = (old_label[0], old_label[1] - 2*np.pi)
                while old_label[1] / np.pi < -1:
                    old_label = (old_label[0], old_label[1] + 2 * np.pi)
                if np.abs(old_label[1]/np.pi) == 1:
                    new_label = new_label
                elif old_label[1] / np.pi == 0.5:
                    new_label = 'SQRT_' + new_label
                elif old_label[1] / np.pi == -0.5:
                    new_label = 'SQRT_' + new_label + '_DAG'
                else:
                    raise ValueError('Do not support theta/np.pi = ', str(old_label[1]/np.pi))
                new_position = self.position_list[ii]
            else:
                raise ValueError('Do not support the label of', str(ii), 'th gate, which is', old_label)
            stim_circuit.append(new_label, new_position)
        return stim_circuit


    def to_cirq(self):
        supported_gates_C = {'CZ':cirq.CZ, 'CX':cirq.CX}
        supported_gates_R = {'RX':cirq.rx, 'RY':cirq.ry, 'RZ':cirq.rz}
        supported_gates_CC = {'CCX':cirq.CCX}
        supported_gates_U = {'U3':QasmUGate}
        cirq_citcuit = cirq.Circuit()
        for ii in range(len(self)):
            if len(self.control_list[ii]) > 0:
                raise ValueError('does not support controlled gates')
            tmp_label = self.gate_list[ii].label
            if tmp_label in supported_gates_C.keys():
                position0 = self.qubit_position[self.position_list[ii][0]]
                position1 = self.qubit_position[self.position_list[ii][1]]
                qubit0 = cirq.GridQubit(position0[0], position0[1])
                qubit1 = cirq.GridQubit(position1[0], position1[1])
                cirq_citcuit.append(supported_gates_C[tmp_label](qubit0, qubit1))
            elif tmp_label in supported_gates_CC.keys():
                position0 = self.qubit_position[self.position_list[ii][0]]
                position1 = self.qubit_position[self.position_list[ii][1]]
                position2 = self.qubit_position[self.position_list[ii][2]]
                qubit0 = cirq.GridQubit(position0[0], position0[1])
                qubit1 = cirq.GridQubit(position1[0], position1[1])
                qubit2 = cirq.GridQubit(position2[0], position2[1])
                cirq_citcuit.append(supported_gates_CC[tmp_label](qubit0, qubit1, qubit2))
            elif tmp_label[0] in supported_gates_R.keys():
                position0 = self.qubit_position[self.position_list[ii][0]]
                qubit0 = cirq.GridQubit(position0[0], position0[1])
                cirq_citcuit.append(supported_gates_R[tmp_label[0]](tmp_label[1])(qubit0))
            elif tmp_label[0] in supported_gates_U.keys():
                position0 = self.qubit_position[self.position_list[ii][0]]
                qubit0 = cirq.GridQubit(position0[0], position0[1])
                theta, phi, lmda = tmp_label[1]
                cirq_citcuit.append(supported_gates_U[tmp_label[0]](theta/np.pi, phi/np.pi, lmda/np.pi)(qubit0))
            else:
                raise ValueError(tmp_label, 'is not supported')
        return cirq_citcuit

    def cirq_qubit_order(self):
        cirq_order_list = []

        for pp in self.qubit_position:
            cirq_order_list.append(cirq.GridQubit(pp[0], pp[1]))
        cirq_order = cirq.QubitOrder.explicit(cirq_order_list)
        return cirq_order

    def draw_circuit_cirq(self, save_path='./cirq.html'):
        cirq_circuit = self.to_cirq()
        c3d = cirq_web.Circuit3D(cirq_circuit)
        c3d.generate_html_file(file_name=save_path)

    def qiskit_draw(self, **kwargs):
        return self.to_qiskit().draw(**kwargs)

    def calculate_connectivity(self):
        qubit_list = []
        qubit_connectivity = []
        for ii in range(len(self)):
            qubit_list.append(self.position_list[ii]+self.control_list[ii])
        for qq in range(self.n_qubit):
            tmp_connectted = list()
            for ii in range(len(self)):
                if qq in qubit_list[ii]:
                    tmp_connectted.extend(qubit_list[ii])
            tmp_connectted = set(tmp_connectted)
            tmp_connectted.discard(qq)
            qubit_connectivity.append((qq, tmp_connectted))
        return qubit_connectivity

    def check_connectivity(self):
        error_list = []
        for _, pp, pp_c in self:
            position_combined = pp + pp_c
            if len(position_combined) > 2:
                raise ValueError('reduce all gate to one- or two- qubit gates before check connectivity')
            if len(position_combined) == 2:
                dis_row = self.qubit_position[position_combined[0]][0] - self.qubit_position[position_combined[1]][0]
                dis_col = self.qubit_position[position_combined[0]][1] - self.qubit_position[position_combined[1]][1]
                ab_dis = np.abs(dis_row) + np.abs(dis_col)
                if ab_dis > 1:
                    error_list.append((pp, pp_c))
        if len(error_list) > 0:
            error_str = 'check connectivity fails. Error list is ' +  str(error_list)
            raise ValueError(error_str)

    def assign_tensor4gates(self, remove_label=False):
        for gg in self.gate_list:
            if gg.label is not None:
                gg.assign_tensor(remove_label=remove_label)
                gg.to(self.device)
                gg.to(self.dtype)
    
    def nearest_nerighbor_coupling_map(self):
        coupling_map = []
        qubit_position = self.qubit_position
        for pp0 in range(self.n_qubit):
            for pp1 in range(self.n_qubit):
                q0 = qubit_position[pp0]
                q1 = qubit_position[pp1]
                if (np.abs(q0[0] - q1[0]) + np.abs(q0[1] - q1[1])) == 1:
                    coupling_map.append([pp0, pp1])
        return coupling_map



def qft(n_qubit, position, control=None, inverse=False, ordering=True, device='cpu', dtype=tc.complex64):
    if control is None:
        control = []
    tmp_circuit = Circuit(n_qubit, device, dtype)
    m_qft = len(position)
    perm = list(range(m_qft))
    perm.reverse()
    theta_list = []
    theta = 2 * np.pi
    for mm in range(m_qft + 1):
        theta_list.append(theta)
        theta = theta / 2
    for mm in range(m_qft):
        tmp_circuit.hadamard([position[mm]])
        for nn in range(mm + 1, m_qft):
            tmp_circuit.phase_shift(position=[position[mm]], theta=theta_list[nn - mm + 1], control=[position[nn]] + control)
    if ordering:
        for mm in range(m_qft // 2):
            tmp_circuit.swap_gate(position=[position[mm], position[- mm - 1]], control=control)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def ch(n_qubit, unitary, position_phi, position_c, control=None, inverse=False, device='cpu', dtype=tc.complex64):
    raise ValueError('waiting to fix')
    if control is None:
        control = []
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if isinstance(unitary, Gate.Gate):
        tmp_gate = Gate.Gate(unitary)
    elif isinstance(unitary, Circuit):
        tmp_gate = copy.deepcopy(unitary)
    else:
        raise TypeError('the unitary should be a gate')
    m_fch = len(position_c)
    for mm in range(m_fch):
        tmp_circuit.compose(tmp_gate, position_phi, [position_c[- mm - 1]] + control, inverse)
        tmp_gate.square()
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def qpe(n_qubit, unitary, position_phi, position_qpe, control=None, inverse=False, device='cpu', dtype=tc.complex64):
    if control is None:
        control = []
    tmp_circuit = Circuit(n_qubit, device, dtype)
    tmp_circuit.hadamard(position_qpe, control=control)
    tmp_circuit.ch(unitary, position_phi, position_qpe, control, False)
    tmp_circuit.qft(position_qpe, control=control, inverse=True)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def qhc(n_qubit, unitary, position_phi, position_qpe, position_f, n_f=None,
        control=None, inverse=False, device='cpu', dtype=tc.complex64):
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    if n_f is None:
        n_f = 2 ** (len(position_f) - 1) - 1
    if n_f > (2 ** len(position_f) - 1) / 2:
        print('warning, n_f is too large')
    for nn in range(n_f):
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.qpe(unitary, position_phi, position_qpe,
                        control=position_f + control, inverse=False)
        # sample(1000, position_qpe)
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.add_one(position_f, [position_qpe[0]] + control, inverse=False)
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.qpe(unitary, position_phi, position_qpe,
                        control=position_f + control, inverse=True)
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.add_one(position_f, control=control, inverse=False)
        tmp_circuit.not_gate(position_qpe, control)
        tmp_circuit.add_one(position_f, control=position_qpe + control, inverse=True)
        tmp_circuit.not_gate(position_qpe, control)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def add_one(n_qubit, position=None, control=None, inverse=False, device='cpu', dtype=tc.complex64):
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    if position is None:
        position = list(range(n_qubit))
    m_a = len(position)
    for mm in range(m_a):
        tmp_circuit.not_gate([position[mm]], control=position[mm + 1:] + control)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def quantum_coin(n_qubit, unitary, position_phi, position_coin, control=None, inverse=False,
                 device='cpu', dtype=tc.complex64):
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    tmp_circuit.hadamard(position_coin, control)
    tmp_circuit.compose(unitary, position_phi, position_coin)
    tmp_circuit.not_gate(position_coin, control)
    tmp_circuit.compose(unitary, position_phi, position_coin, True)
    # self.phase_shift(-eig_value, position_coin, control)
    tmp_circuit.not_gate(position_coin, control)
    tmp_circuit.hadamard(position_coin, control)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit


def qdc(n_qubit, unitary, position_phi, position_coin, position_f, n_f=None,
        control=None, inverse=False, device='cpu', dtype=tc.complex64):
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    if n_f is None:
        n_f = 2 ** (len(position_f) - 1) - 1
    if n_f > (2 ** len(position_f) - 1):
        print('warning, n_f is too large')
    for nn in range(n_f):
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.quantum_coin(unitary, position_phi, position_coin, control=position_f + control, inverse=False)
        tmp_circuit.not_gate(position_f, control)
        tmp_circuit.add_one(position_f, position_coin + control, inverse=False)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit

def adder(n_qubit, p_add_1, p_add_2, control=None, inverse=False, device='cpu', dtype=tc.complex64):
    # For n qubits in p_add_1, the number smaller than 2^(n-2) - 1 is postive, and the number larger 
    # than 2^(n-1) is negative. The interval is for the sum of two large integers. The results are stored in p_add_1.
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    n_add_1 = len(p_add_1)
    n_add_2 = len(p_add_2)
    # assert n_add_1 == n_add_2
    tmp_circuit.qft(position=p_add_1, ordering=False)
    theta0 = 2 * np.pi / 2 ** n_add_1
    for ii in range(n_add_2):
        for jj in range(n_add_1):
            tmp_theta = theta0 * (2 ** (ii + jj))
            if (ii + jj) < n_add_1:
                tmp_circuit.phase_shift(position=[p_add_1[jj]], theta=tmp_theta, control=[p_add_2[-ii - 1]]+control)
    tmp_circuit.qft(position=p_add_1, ordering=False, inverse=True)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit

def subtractor(n_qubit, p_add_1, p_add_2, control=None, inverse=False, device='cpu', dtype=tc.complex64):
    # For n qubits in p_add_1, the number smaller than 2^(n-2) - 1 is postive, and the number larger
    # than 2^(n-1) is negative. The interval is for the sum of two large integers. The results are stored in p_add_1.
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    n_add_1 = len(p_add_1)
    n_add_2 = len(p_add_2)
    # assert n_add_1 == n_add_2
    tmp_circuit.qft(position=p_add_1, ordering=False)
    theta0 = 2 * np.pi / 2 ** n_add_1
    for ii in range(n_add_2):
        for jj in range(n_add_1):
            tmp_theta = theta0 * (2 ** (ii + jj))
            if (ii + jj) < n_add_1:
                tmp_circuit.phase_shift(position=[p_add_1[jj]], theta=-tmp_theta, control=[p_add_2[-ii - 1]]+control)
    tmp_circuit.qft(position=p_add_1, ordering=False, inverse=True)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit

def multiplicator(n_qubit, p_mul_1, p_mul_2, p_result,control=None, inverse=False, device='cpu', dtype=tc.complex64):
    tmp_circuit = Circuit(n_qubit, device, dtype)
    if control is None:
        control = []
    n_mul_1 = len(p_mul_1)
    n_mul_2 = len(p_mul_2)
    n_result = len(p_result)
    tmp_circuit.hadamard(position=p_result, control=control)
    theta0 = 2 * np.pi / 2 ** n_result
    for ii in range(n_mul_1):
        for jj in range(n_mul_2):
            for kk in range(n_result):
                tmp_theta = theta0 * (2 ** (ii + jj + kk))
                if  (ii + jj + kk) < n_result:
                    tmp_circuit.phase_shift(position=[p_result[kk]], theta=tmp_theta, control=[p_mul_1[-ii - 1]]+[p_mul_2[-jj-1]]+control)
    tmp_circuit.qft(position=p_result, ordering=False, inverse=True)
    if inverse:
        tmp_circuit.inv()
    return tmp_circuit