import cirq
from optimization.optimize_circuits import CircuitIdentity
from .transfer_flag_optimizer import TransferFlagOptimizer
import quantify.utils.misc_utils as mu


class CancelNghCNOTs(TransferFlagOptimizer):
    # Cancels two neighbouring CNOTs

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

        if mu.my_isinstance(op, cirq.CNOT):

            if self.transfer_flag and (not mu.has_flag(op)):
                # Optimize only flagged operations
                return None

            """
            Checking for the CNOTs
            """
            control_qubit = op.qubits[0]
            target_qubit = op.qubits[1]

            # is the next gate a cnot?
            nxt_1 = circuit.next_moment_operating_on([control_qubit],
                                                     start_moment_index=index + 1)
            if nxt_1 is None:
                return None

            nxt_2 = circuit.next_moment_operating_on([target_qubit],
                                                     start_moment_index=index + 1)
            if nxt_2 is None:
                return None

            # Get the operation at the next index
            next_op_cnot1 = circuit.operation_at(control_qubit, nxt_1)
            next_op_cnot2 = circuit.operation_at(target_qubit, nxt_2)

            # print("next are ", next_op_h1, next_op_h2)

            # Are the operations Hadamards?
            if mu.my_isinstance(next_op_cnot1, cirq.CNOT) and mu.my_isinstance(next_op_cnot2, cirq.CNOT):

                # theoretically nxt_1 and nxt_2 should be equal
                if nxt_1 != nxt_2:
                    return None

                if next_op_cnot1 != next_op_cnot2:
                    return None

                if self.transfer_flag and (not mu.has_flag(next_op_cnot1)):
                    # Optimize only flagged operations
                    return None

                if self.transfer_flag:
                    mu.transfer_flags(circuit, op.qubits[0], index, nxt_1)

                if self.only_count:
                    self.count += 1
                    self.moment_index_qubit.append((CircuitIdentity.CANCEL_CNOTS.value, index, op.qubits[0]))
                    return None

                return cirq.PointOptimizationSummary(
                    clear_span=nxt_1 - index + 1,  # Range of moments to affect.
                    clear_qubits=op.qubits,  # The set of qubits that should be cleared with each affected moment
                    new_operations=[]  # The operations to replace
                )
