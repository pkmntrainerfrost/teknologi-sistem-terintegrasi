from typing import List
from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
from pathlib import Path

from ..tags import tags

class CommissionSlot(BaseModel):
	commissionslot_id: int
	user_id: int
	slot_no: int
	status: str
	title: str 
	commissionslot_type: str # stupid python reserved word
	desc_general: str
	desc_do: str
	desc_dont: str
	tags: List[tags.AppliedTag]
	community_tags: bool
	price_lowerbound: float
	commissionstaken: int
	rating: float

app = FastAPI()

json_path = Path(__file__).parent.parent / "data" / "commissionslots.json"

with json_path.open() as file:
 	data = json.load(file)

# Core Service

# Commission Slot Search Engine (WIP)
@app.get("/commissionslots/")
async def read_all_commissionslots():

    params = locals()

    filtered_data = []
                

    # Regex /

    # Title

    # 

# Generic Services

# Get commission slot by ID
@app.get("/commissionslots/{commissionslot_id}")
async def read_commission(commissionslot_id: int):
	
	for commissionslot_item in data['commissionslots']:
		
		print(commissionslot_item)
		if commissionslot_item['id'] == commissionslot_id:
			return commissionslot_item
		
	raise HTTPException (
		status_code=404, detail=f'Commission slot with id {commissionslot_id} not found'
	)

# Add commission slot
@app.post('/commissionslots')
async def add_commissionslot(commissionslot: CommissionSlot):
	commissionslot_dict = commissionslot.dict()
	commissionslot_found = False
	for commissionslot_item in data['comissionslots']:
		if commissionslot_item['id'] == commissionslot_dict['id']:
			commissionslot_found = True
			return "Commission slot with ID "+str(commissionslot['id'])+" exists."
	
	if not commissionslot_found:
		data['comissionslots'].append(commissionslot_dict)
		with json_path.open(mode="w") as write_file:
			json.dump(data, write_file)

		return commissionslot_dict
	
	raise HTTPException(
		status_code=404, detail=f'Commission slot not found'
	)

# Update commission slot
@app.put('/commissionslots')
async def update_commissionslot(commissionslot: CommissionSlot):
	commissionslot_dict = commissionslot.dict()
	commissionslot_found = False
	for commissionslot_idx, commissionslot_item in enumerate(data['commissionslots']):
		if commissionslot_item['id'] == commissionslot_dict['id']:
			commissionslot_found = True
			data['commissionslots'][commissionslot_idx]=commissionslot_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "Commission slot updated"
	
	if not commissionslot_found:
		return "Commission slot ID not found"
	raise HTTPException(
		status_code=404, detail=f'Commission slot not found'
	)

# Delete commission slot
@app.delete('/commissionslots/{commissionslot_id}')
async def delete_menu(commissionslot_id: int):

	commissionslot_found = False
	for commissionslot_idx, commissionslot_item in enumerate(data['commissionslots']):
		if commissionslot_item['id'] == commissionslot_id:
			commissionslot_found = True
			data['commissionslots'].pop(commissionslot_idx)
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "Commission slot deleted"
	
	if not commissionslot_found:
		return "Commission slot ID not found"
	raise HTTPException(
		status_code=404, detail=f'Commission slot not found'
	)

# Add tag
@app.post('/commissionslots/{commissionslot_id}/tags')
async def add_menu(commissionslot_id: int, tag: tags.AppliedTag):
	tag_dict = tag.dict()
	commissionslot_found = False

	for commissionslot_idx, commissionslot_item in enumerate(data['commissionslots']):
		if commissionslot_item['id'] == commissionslot_id:
			commissionslot_found = True
			tag_found = False
			for tag_item in commissionslot_item["tags"]:
				if tag_item['id'] == tag_dict['id']:
					tag_found = True
					return "Tag with ID "+str(tag_dict['id'])+" exists."
				elif tag_item['tag'] == tag_dict['tag']:
					tag_found = True
					return "Tag with name "+tag_dict['tag']+" exists."
			if commissionslot_found and not tag_found:
				data["commissionslots"][commissionslot_idx]["tags"].append(tag_dict)
				with open(json_filename,"w") as write_file:
					json.dump(data, write_file)
				return "Tag added."
	
	if not commissionslot_found:
		return "Commission slot ID not found"
	raise HTTPException(
		status_code=404, detail=f'Commission slot not found'
	)

# Tag voting
@app.post('/commissionslots/{commissionslot_id}/tags/{tag_id}/vote')
async def add_menu(commissionslot_id: int, tag_id: int, vote: int):
	commissionslot_found = False
	for commissionslot_idx, commissionslot_item in enumerate(data['commissionslots']):
		if commissionslot_item['id'] == commissionslot_id:
			commissionslot_found = True
			tag_found = False
			for tag_idx, tag_item in enumerate(commissionslot_item["tags"]):
				if tag_item['id'] == tag_id:
					tag_found = True
					if vote == 1:
						data['commissionslots'][commissionslot_idx]["tags"][tag_idx]["votes"] += 1
					elif vote == 0:
						data['commissionslots'][commissionslot_idx]["tags"][tag_idx]["votes"] -= 1
					else:
						return "Invalid vote."
					with open(json_filename,"w") as write_file:
						json.dump(data, write_file)
					return "Vote added."
	
	if not commissionslot_found:
		return "Commission slot ID not found"
	if not tag_found:
		return "Tag ID not found"
	raise HTTPException(
		status_code=404, detail=f'Commission slot not found'
	)
