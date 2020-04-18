function OnStoredInstance(instanceId, tags, metadata)

-- Assumes only CXRs that are predicted are sent to the Orthanc instance. 
-- Therefore there are no additional filters here.
  if tags["SeriesDescription"] ~= "COVID-Net Prediction" then
	print("Predicting:" .. instanceId)
	file = io.open("InstanceToBePredicted/" .. instanceId, "w")
	file:write(instanceId)
	file:close()
  end

-- Uncomment the following block to send the DICOM instance of the prediction back to PACS
-- (TODO: Limit retry attempts and log error somewhere)
-- Example of PACS here is "PLAZASERVER", which can be set within orthanc.json
--[[
  if tags["SeriesDescription"] == "COVID-Net Prediction" then
	response = nil
	attempt = 0
	while (response == nil)
	do
		print("Routing Using POST:" .. tags["SeriesDescription"] .. "(Attempt: " .. attempt .. ")")
		response = RestApiPost("/modalities/PLAZASERVER/store", instanceId)
		print(response)
		attempt = attempt + 1
	end
  end  
--]]
end