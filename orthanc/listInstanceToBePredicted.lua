function OnStoredInstance(instanceId, tags, metadata)

  if tags["SeriesDescription"] ~= "COVID-Net Prediction" then
	print("Predicting:" .. instanceId)
	file = io.open("InstanceToBePredicted/" .. instanceId, "w")
	file:write(instanceId)
	file:close()
  end

  if tags["SeriesDescription"] == "COVID-Net Prediction" then
	print("Routing: " .. tags["SeriesDescription"])
    SendToModality(instanceId, 'VIA102077')
  end  

end