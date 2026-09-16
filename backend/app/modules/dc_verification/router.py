
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.integrations.mail.client import send_deviation_email
from app.modules.deviations.models import Deviation
from app.modules.dc_verification.schemas import DcVerificationRequest, DcVerificationResponse
from app.modules.dc_verification.service import DcVerificationError, verify_delivery_challan

router = APIRouter(prefix="/dc-verification", tags=["dc_verification"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"module": "M5 DC Verification", "status": "not_yet_implemented"}


@router.post("/{dc_no}/verify", response_model=DcVerificationResponse)
async def verify_dc(
    dc_no: str,
    payload: DcVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DcVerificationResponse:
    try:
        result = await verify_delivery_challan(
            db, dc_no, payload.actual_front_case, payload.actual_back_case
        )
        await db.commit()
    except DcVerificationError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    vendor_email = result.pop("vendor_email", None)

    if result["deviation_created"]:
        # Reflect the actual outcome on the deviation record itself — this
        # is what M7's list screen displays under "Vendor Notified", so it
        # needs to say something real rather than always "pending".
        deviation_result = await db.execute(select(Deviation).where(Deviation.id == result["deviation_id"]))
        deviation = deviation_result.scalar_one()

        if vendor_email:
            deviation.mail_status = "sent"
            await db.commit()
            # Fire-and-forget per architecture doc Section 5.2 — vendor email
            # shouldn't block the verification response.
            background_tasks.add_task(
                send_deviation_email,
                to_address=vendor_email,
                dc_no=result["dc_no"],
                difference_qty=result["expected_qty"] - result["actual_qty"],
            )
        else:
            deviation.mail_status = "no_email_on_file"
            await db.commit()
            # Vendor has no email on file yet — don't silently drop this.
            # Masters (M15) needs to be updated with the vendor's email
            # before this deviation notification can actually be sent.
            print(
                f"[dc_verification] WARNING: deviation created for DC {result['dc_no']} "
                "but vendor has no email on file — notification NOT sent"
            )

    return DcVerificationResponse(**result)







