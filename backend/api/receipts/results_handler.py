from typing import List, Dict, Tuple, Optional


def get_highest_confidence(target: List[Dict[str, float]]) -> Optional[str]:
    if not target:
        return None
    max_dict = max(target, key=lambda d: list(d.keys())[0])
    return list(max_dict.values())[0]


def process_field(field: Dict[str, dict]) -> Tuple[str, Dict[str, dict]]:
    text = field.get("Type", {}).get("Text", "")
    confidence = field.get("Type", {}).get("Confidence", 0.0)
    value_detection = field.get("ValueDetection", {})
    currency_code = field.get("Currency", {}).get("Code", "")
    label_detection_text = field.get("LabelDetection", {}).get("Text", "")

    if text == "VENDOR_NAME":
        return text, {confidence: value_detection.get("Text", "")}
    elif text in ("TOTAL", "AMOUNT_PAID"):
        total = {
            "total": value_detection.get("Text", ""),
            "currency": currency_code,
        }
        return text, {confidence: total}
    elif text == "INVOICE_RECEIPT_DATE":
        return text, {confidence: value_detection.get("Text", "")}
    elif text == "OTHER" and label_detection_text == "CHANGE DUE":
        return text, {confidence: value_detection.get("Text", "")}
    else:
        return "UNKNOWN", {}


def parse_analysis(response: Dict[str, List[Dict[str, dict]]]) -> Dict[str, str]:
    field_map: Dict[str, List[Dict[str, dict]]] = {
        "VENDOR_NAME": [],
        "TOTAL": [],
        "INVOICE_RECEIPT_DATE": [],
        "AMOUNT_PAID": [],
        "OTHER": [],
    }

    for expense_document in response.get("ExpenseDocuments", []):
        summary_fields = expense_document.get("SummaryFields", [])
        for field in summary_fields:
            field_text, field_data = process_field(field)
            if field_text in field_map:
                field_map[field_text].append(field_data)

    highest_values: Dict[str, str] = {}
    for field_text, field_list in field_map.items():
        highest_values[field_text] = get_highest_confidence(field_list)

    return highest_values
