from backend.models import MonthlyReport, User, Organization
from backend.core.utils.dataclasses import BaseServiceResponse


class GetReportServiceResponse(BaseServiceResponse[MonthlyReport]): ...


def get_report(owner: User | Organization, uuid) -> GetReportServiceResponse:
    report = MonthlyReport.filter_by_owner(owner).filter(uuid=uuid).first()

    if report:
        return GetReportServiceResponse(True, report)
    else:
        return GetReportServiceResponse(False, error_message="Report not found")
