from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from beanie import PydanticObjectId, Link
from typing import List
from app.schemas.schemas import CommissionSlotCreate, CommissionSlotUpdate, CommissionCreate
from app.models.models import CommissionSlot, User, Commission, Df, TfIdf
from app.auth.user import current_active_user
from app.utils.preprocess import preprocess
from bson.dbref import DBRef
from nltk.tokenize import word_tokenize

from collections import Counter

import numpy

router = APIRouter()

# Get all commissionslots (Generic/CRUD) - narrow and sort based on parameters (Generic/CRUD) and search engine (CORE)
@router.get("/")
async def read_all_commissionslots(query : str | None = None):
    
    if query != None:
        split_query = query.split(" ")

        tags = [word for word in split_query if word.startswith("#")]
        word_query = [word for word in split_query if not word.startswith("#")]

        if word_query != []:
            tokens = preprocess(" ".join(word_query))
        else:
            tokens = []
        
        if (tokens != []):
            if (tags != []):
                commissionslots = await CommissionSlot.find({"tags" : {"$all" : tags},"desc_general_preprocessed": {"$in": tokens}}).to_list()
            else:
                commissionslots = await CommissionSlot.find({"desc_general_preprocessed" : {"$in": tokens}}).to_list()
            matching_docs_ids = [str(x.id) for x in commissionslots]
            matchingscore = dict.fromkeys(matching_docs_ids,0)
            for token in tokens:
                tfidf_docs = await TfIdf.find(TfIdf.token == token).to_list()
                for tfidf_doc in tfidf_docs:
                    if tfidf_doc.slot in matching_docs_ids:
                        matchingscore[tfidf_doc.slot] += tfidf_doc.value
            sorted_commissionslots = sorted(commissionslots, key=lambda x: matchingscore[str(x.id)], reverse=True)
            commissionslots = sorted_commissionslots
        elif (tags != []):
            commissionslots = await CommissionSlot.find({"tags" : {"$all" : tags}}).to_list()
        else:
            commissionslots = await CommissionSlot.find().to_list()
    else:
        commissionslots = await CommissionSlot.find().to_list()

    return commissionslots


# Get commissionslot by ID (CRUD)
@router.get("/{commissionslot_id}")
async def read_commissionslot_by_id(id: str) -> CommissionSlot:
    
    commissionslot = await CommissionSlot.get(PydanticObjectId(id),fetch_links=True)
    return commissionslot

# Post commissionslot (CRUD)
@router.post("/",status_code=201)
async def create_commissionslot(commissionslot_input : CommissionSlotCreate, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)

    try:
        slot_number = await CommissionSlot.find({"user.$id" : PydanticObjectId(id)}).sort(-CommissionSlot.slot_number).first_or_none()
        slot_number = slot_number.slot_number
        slot_number += 1
    except:
        slot_number = 1

    new_tags = commissionslot_input.tags

    if commissionslot_input.tags != None:
        bad_tags = [tag for tag in commissionslot_input.tags if ((not tag.startswith("#")) or " " in tag)]
        if bad_tags != []:
            raise HTTPException(status_code=400, detail="BAD")
        new_tags = [tag.lower() for tag in commissionslot_input.tags]

    title_preprocessed = preprocess(commissionslot_input.title)
    desc_general_preprocessed = preprocess(commissionslot_input.desc_general)

    commissionslot = CommissionSlot(
        user = id,
        slot_number = slot_number,
        status = "OPEN",
        worktype = commissionslot_input.worktype,
        title = commissionslot_input.title,
        title_preprocessed = preprocess(commissionslot_input.title),
        desc_general = commissionslot_input.desc_general,
        desc_general_preprocessed = preprocess(commissionslot_input.desc_general),
        desc_do = commissionslot_input.desc_do,
        desc_dont = commissionslot_input.desc_dont,
        community_tags = commissionslot_input.community_tags,
        tags = new_tags,
        price_lowerbound = commissionslot_input.price_lowerbound,
        price_upperbound = commissionslot_input.price_upperbound,
        commissions_taken = 0,  
        rating = 0  
    )

    x = await commissionslot.insert()

    tokens = []
    for token in title_preprocessed + desc_general_preprocessed:
        if token not in tokens:
            tokens += [token]
            
    for token in tokens:

        df = await Df.find_one(Df.token == token)

        if df:
            z = df.slots
            z = z + [str(x.id)]
            await df.set({Df.slots : z})
        else:
            df = Df(token=token, slots=[str(x.id)])
            await df.insert()

    return x
    
# Edit commissionslot
@router.put("/{commissionslot_id}")
async def update_commissionslot(commissionslot_id : str, commissionslot_input : CommissionSlotUpdate, user: User = Depends(current_active_user)):

    commissionslot = await CommissionSlot.get(PydanticObjectId(commissionslot_id))

    if not commissionslot:
        raise HTTPException(status_code=404, detail="CommissionSlot not found")
    
    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)

    if (commissionslot.user != id) or (not user.is_superuser):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if commissionslot_input.tags != None:
        bad_tags = [tag for tag in commissionslot_input.tags if ((not tag.startswith("#")) or " " in tag)]
        if bad_tags != None:
            raise HTTPException(status_code=400, detail="BAD")
        new_tags = [tag.lower() for tag in commissionslot_input.tags]
    
    new_tokens = []

    old_title_preprocessed = commissionslot.title_preprocessed
    old_desc_general_preprocessed = commissionslot.desc_general_preprocessed
    
    for field, value in commissionslot_input.dict(exclude_unset=True).items():

        setattr(commissionslot, field, value)

        if field == "desc_general":
            new_desc_general_preprocessed = preprocess(value)
            commissionslot.desc_general_preprocessed = new_desc_general_preprocessed
            if new_tokens == []:
                new_tokens = new_desc_general_preprocessed
            else:
                new_tokens += [token for token in new_desc_general_preprocessed if token not in new_tokens]
        if field == "title":
            new_title_preprocessed = preprocess(value)
            commissionslot.title_preprocessed = new_title_preprocessed
            if new_tokens == []:
                new_tokens = new_title_preprocessed
            else:
                new_tokens += [token for token in new_title_preprocessed if token not in new_tokens]

    old_tokens = []
    for token in old_title_preprocessed + old_desc_general_preprocessed:
        if token not in old_tokens:
            old_tokens += [token]

            
    added_tokens = [token for token in new_tokens if token not in old_tokens]
    deleted_tokens = [token for token in old_tokens if token not in new_tokens]


    for token in added_tokens:

        df = await Df.find_one(Df.token == token,fetch_links=True)

        if df:
            z = df.slots + [commissionslot_id]
            await df.set({Df.slots : z})
        else:
            df = Df(token=token, slots=[commissionslot_id])
            await df.insert()
    
    for token in deleted_tokens:

        df = await Df.find_one(Df.token == token,fetch_links=True)

        if df:
            z = [obj for obj in df.slots if obj != commissionslot_id]
            print(z)
            if len(z) == 0:
                await df.delete()
            else:
                await df.set({Df.slots : z})

    # Save the updated CommissionSlot
    await commissionslot.save()

    return commissionslot

# Delete commissionslot (superuser only)
@router.delete("/{commissionslot_id}")
async def delete_commissionslot(commissionslot_id : str, user: User = Depends(current_active_user)):

    commissionslot = await CommissionSlot.get(PydanticObjectId(commissionslot_id),fetch_links=True)

    if not commissionslot:
        raise HTTPException(status_code=404, detail="CommissionSlot not found")
    
    user = await User.find(User.username == user.username).first_or_none()
    id = user.id


    if (commissionslot.user.id != id) or (not user.is_superuser):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Save the updated CommissionSlot
    await CommissionSlot.get(PydanticObjectId(commissionslot_id)).delete()

# Propose commission
@router.post("/{commissionslot_id}/proposeCommission")
async def create_commission(commissionslot_id : str, commission_input : CommissionCreate, user: User = Depends(current_active_user)):

    user = await User.find(User.username == user.username).first_or_none()
    id = str(user.id)    

    commissionslot = await CommissionSlot.get(PydanticObjectId(commissionslot_id))

    if (commissionslot.user == id):
        raise HTTPException(status_code=403, detail="You can't propose a commission to your own slot")
        
    commission = Commission(
        commissionslot = commissionslot_id,
        commissioner = id,
        commissionee = commissionslot.user,
        description = commission_input.description,
        description_preprocessed = preprocess(commission_input.description),
        feedback = "",
        status = "WAITING",
        rating_overall = 0,
        rating_quality = 0,
        rating_match = 0,
        rating_timeliness = 0,
    )

    await commission.insert()

    return commission

# Update TF-IDF value
@router.put("/refresh_tf_idf/")
async def refresh_tf_idf():

    dfs = await Df.find_all().to_list()

    words = [x.token for x in dfs]
    freq = [len(x.slots) for x in dfs]

    docfreq = {k:v for (k,v) in zip(words,freq)}

    wordcount = len(dfs)

    commissionslots = await CommissionSlot.find_all().to_list()

    print(wordcount)

    title_tf_idf = {}
    desc_tf_idf = {}
    commissions_tf_idf = {}
    tf_idf = {}

    for commissionslot in commissionslots:

        tokens_title = commissionslot.title_preprocessed
        tokens_desc = commissionslot.desc_general_preprocessed
        
        finished_commissions = await Commission.find(Commission.commissionslot == str(commissionslot.id), Commission.status == "FINISHED", Commission.rating_overall != 0).to_list()

        commissions_descs = [x.description_preprocessed for x in finished_commissions]
        tokens_commissions = [token for desc in commissions_descs for token in desc]

        counter = Counter(tokens_title + tokens_desc + tokens_commissions)
        
        for token in numpy.unique(tokens_title):
            title_tf = counter[token]/wordcount
            title_df = docfreq[token]
            title_idf = numpy.log((wordcount+1)/(title_df+1))
            title_tf_idf[str(commissionslot.id),token] = title_tf * title_idf

        for token in numpy.unique(tokens_desc):
            desc_tf = counter[token]/wordcount
            desc_df = docfreq[token]
            desc_idf = numpy.log((wordcount+1)/(title_df+1))
            desc_tf_idf[str(commissionslot.id),token] = desc_df * desc_idf

        for token in numpy.unique(tokens_commissions):
            commissions_tf = counter[token]/wordcount
            commissions_df = docfreq[token]
            commissions_idf = numpy.log((wordcount+1)/(title_df+1))
            commissions_tf_idf[str(commissionslot.id),token] = commissions_df * commissions_idf

        for token in numpy.unique(tokens_title + tokens_desc + tokens_commissions):
            
            tf_idf = 0

            if len(commissions_tf_idf) == 0:
                try:
                    tf_idf += title_tf_idf[str(commissionslot.id),token] * 0.7
                except:
                    pass
                try:
                    tf_idf += desc_tf_idf[str(commissionslot.id),token] * 0.3
                except:
                    pass
            else:
                try:
                    tf_idf += title_tf_idf[str(commissionslot.id),token] * 0.63
                except:
                    pass
                try:
                    tf_idf += desc_tf_idf[str(commissionslot.id),token] * 0.27
                except:
                    pass
                try:
                    tf_idf += commissions_tf_idf[str(commissionslot.id),token] * 0.1
                except:
                    pass
        
            new_tf_idf = TfIdf(slot=str(commissionslot.id),token=token,value=tf_idf)
            await new_tf_idf.insert()
