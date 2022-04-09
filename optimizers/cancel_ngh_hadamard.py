from typing import List, Tuple

import cirq

import quantify.utils.misc_utils as mu
from optimization.optimize_circuits import CircuitIdentity
from .transfer_flag_optimizer import TransferFlagOptimizer


class CancelNghHadamards(TransferFlagOptimizer):

    def __init__(self, moment=None, qubits=None, only_count=False, count_between=False):
        super().__init__()
        self.only_count: bool = only_count
        self.count: int = 0
        self.moment_index_qubit: List[Tuple[int, int, List[cirq.Qid]]] = []
        self.moment: int = moment
        self.qubits: List[cirq.NamedQubit] = qubits
        self.start_moment: int = 0
        self.end_moment: int = 0
        self.count_between: bool = count_between

    def optimization_at(self, circuit, index, op):

        if self.count_between and (index < self.start_moment or index > self.end_moment):
            return None

        if (index != self.moment or op.qubits[0] not in self.qubits) and not self.only_count and not self.count_between:
            return None

        # if index != self.moment and not self.only_count and not self.count_between:
        #     return None

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

            if self.count_between:
                self.count += 1
                return None

            if self.only_count:
                self.count += 1
                self.moment_index_qubit.append((CircuitIdentity.CANCEL_HADAMARDS.value, index, [op.qubits[0]]))
                return None

            return cirq.PointOptimizationSummary(clear_span=n_idx - index + 1,
                                                 clear_qubits=op.qubits,
                                                 new_operations=[])

        return None
