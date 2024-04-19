from typing import List

from mypy_boto3_stepfunctions.type_defs import StateMachineListItemTypeDef

from infrastructure.aws.handler import get_sfn_client, DEBUG_LEVEL
from settings.settings import AWS_TAGS_APP_NAME


def get_step_function() -> None | StateMachineListItemTypeDef:
    if DEBUG_LEVEL == "debug":
        print("[AWS] [SFN] Fetching scheduler step function by name...", flush=True)

    sfn_client = get_sfn_client()
    functions = sfn_client.list_state_machines()

    invoice_functions: list[StateMachineListItemTypeDef] = [
        function for function in functions.get("stateMachines", []) if function.get("name") == f"{AWS_TAGS_APP_NAME}-scheduled-invoices"
    ]

    if len(invoice_functions) == 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] [SFN] Found scheduler step function!", flush=True)
        return invoice_functions[0]

    if len(invoice_functions) > 1:
        if DEBUG_LEVEL == "debug":
            print("[AWS] [SFN] Found more than one scheduler step function! Not yet implemented a way to filter.", flush=True)
        raise Exception("More than one invoice scheduler function found. Not yet implemented a way to filter.")

    raise Exception("No invoice scheduler function found. Run `pulumi up` and try again.")
