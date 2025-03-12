SELECT Year, HcpId, Age, WorksiteId, PracticeArrName, SpecialtyName, WkWeeks, WkHours, Fte
FROM @yearEndTable
WHERE TypeId = 'DDS'
	AND Activity = 'Private Practice'