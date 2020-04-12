function OnStoredInstance(instanceId, tags, metadata)
  print(tags["SeriesDescription"])
  if tags["SeriesDescription"] ~= "COVID-Net Prediction" then
	print(instanceId)
	file = io.open("InstanceToBePredicted/" .. instanceId, "w")
	file:write(instanceId)
	file:close()
  end
end