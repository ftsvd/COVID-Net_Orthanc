function OnStoredInstance(instanceId, tags, metadata)

  if tags["SeriesDescription"] ~= "COVID-Net Prediction" then
	print("Predicting:" .. instanceId)
	file = io.open("InstanceToBePredicted/" .. instanceId, "w")
	file:write(instanceId)
	file:close()
  end

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

end