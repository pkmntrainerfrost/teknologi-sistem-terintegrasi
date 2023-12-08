from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from beanie import PydanticObjectId
from typing import List
from app.schemas.schemas import CommissionSlotCreate, CommissionSlotUpdate, CommissionFeedback
from app.models.models import CommissionSlot, User, Commission, Df
from app.auth.user import current_active_user
from app.utils.preprocess import preprocess

router = APIRouter()

@router.get("/{commission_id}")
async def read_comission_by_id(id: PydanticObjectId) -> Commission:
    commissionslot = await Commission.get(id)
    return commissionslot

# Take commission
@router.put("/{commission_id}/take")
async def create_commission(commission_id : str, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commission = await Commission.get(PydanticObjectId(commission_id))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissionee != id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if (commission.status != "WAITING"):
        raise HTTPException(status_code=403, detail="You can't take this commission")

    commission.status = "TAKEN"

    await commission.save()

@router.put("/{commission_id}/reject")
async def reject_commission(commission_id : str, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commission = await Commission.get(PydanticObjectId(commission_id))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissionee != id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if (commission.status != "WAITING"):
        raise HTTPException(status_code=403, detail="You can't reject this commission")

    commission.status = "REJECTED"

    await commission.save()

@router.put("/{commission_id}/finish")
async def finish_commission(commission_id : str, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commission = await Commission.get(PydanticObjectId(commission_id))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissionee != id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if (commission.status != "TAKEN"):
        raise HTTPException(status_code=403, detail="You can't finish this commission")

    commission.status = "FINISHED"

    await commission.save()

@router.put("/{commission_id}/givefeedback")
async def finish_commission(commission_id : str, feedback : CommissionFeedback, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)

    commission = await Commission.get(PydanticObjectId(commission_id))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissioner != id):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if (commission.status != "FINISHED"):
        raise HTTPException(status_code=400, detail="This commission is not finished yet")

    if (commission.rating_overall != 0):
        raise HTTPException(status_code=400, detail="This commission has already been rated") 

    total = 0
    for field, value in feedback.dict(exclude_unset=True).items():

        if field != "feedback":
            if value < 1 or value > 5:
                raise HTTPException(status_code=400, detail="BAD")
            total += value

        setattr(commission, field, value)

    commission.rating_overall = total/3

    tokens = []
    for token in commission.description_preprocessed:
        if token not in tokens:
            tokens += [token]

    for token in tokens:

        df = await Df.find_one(Df.token == token,fetch_links=True)
        z = []

        if df:
            z = [slot for slot in df.slots]
            if commission.commissionslot not in z:
                z += [commission.commissionslot]
            await df.set({Df.slots : z})
        else:
            df = Df(token=token, slots=[commission.commissionslot])
            await df.insert()

    commissionslot = await CommissionSlot.get(PydanticObjectId(commission.commissionslot))

    commissionslot.rating = ( (commissionslot.rating * commissionslot.commissions_taken) + (total/3)) / (commissionslot.commissions_taken + 1)
    commissionslot.commissions_taken += 1

    await commissionslot.save()

    await commission.save()

# Integration

@router.put("/{commission_id}/attachfurniture")
async def attach_furniture(commission_id : str, furniture : int, user : User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commission = await Commission.get(PydanticObjectId(commission_id))
    commissionslot = await CommissionSlot.get(PydanticObjectId(commission.commissionslot))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissioner != id):
        raise HTTPException(status_code=401, detail="Unauthorized")

    
    if (commissionslot.worktype != "FURNITURE"):
        raise HTTPException(status_code=403, detail="You can't attach furniture to this commission")

    return await commission.update({"$set": {"furniture":furniture}})

@router.get("/{commission_id}/furniture_model")
async def get_furniture_model(commission_id : str, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commission = await Commission.get(PydanticObjectId(commission_id))
    commissionslot = await CommissionSlot.get(PydanticObjectId(commission.commissionslot))

    if not commission:
        raise HTTPException(status_code=404, detail="Commission not found")

    if (commission.commissioner != id) and (commission.commissionee != id):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if (commissionslot.worktype != "FURNITURE"):
        raise HTTPException(status_code=403, detail="This is not a furniture commission")

    x = await get_furniture_model(commission.furniture)
    print(x)

    return x