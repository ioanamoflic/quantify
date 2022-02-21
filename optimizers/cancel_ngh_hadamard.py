import cirq

import quantify.utils.misc_utils as mu
from optimization.optimize_circuits import CircuitIdentity
from .transfer_flag_optimizer import TransferFlagOptimizer


class CancelNghHadamards(TransferFlagOptimizer):

    def __init__(self, moment=None, qubit=None, only_count=False):
        super().__init__()
        self.only_count = only_count
        self.count = 0
        self.moment_index_qubit = []
        self.moment = moment
        self.qubit = qubit

    def optimization_at(self, circuit, index, op):
        if (index != self.moment or op.qubits[0] != self.qubit) and not self.only_count:
            return None

        if not (mu.my_isinstance(op, cirq.H)):
            return None

        if self.transfer_flag and (not mu.has_flag(op)):
            # Optimize only flagged operations
            return None

        n_idx = circuit.next_moment_operating_on(op.qubits, index + 1)
        if n_idx is None:
            return None

        next_op = circuit.operation_at(op.qubits[0], n_idx)

        if next_op.gate == cirq.H:
            if self.transfer_flag and (not mu.has_flag(next_op)):
                # Optimize only flagged operations
                return None

            if self.transfer_flag:
                mu.transfer_flags(circuit, op.qubits[0], index, n_idx)

            if self.only_count:
                self.count += 1
                self.moment_index_qubit.append((CircuitIdentity.CANCEL_HADAMARDS, index, op.qubits[0]))
                return None

            # print('Hadamards cancelled ', index)
            return cirq.PointOptimizationSummary(clear_span=n_idx - index + 1,
                                                 clear_qubits=op.qubits,
                                                 new_operations=[])

        return None
