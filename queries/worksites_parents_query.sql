SELECT w.WorksiteId, w.ParentWorksite as ParentId, pa.PracticeArrName
FROM Worksite w
LEFT JOIN WorksiteDetail wd
	ON w.WorksiteId = wd.WorksiteId
LEFT JOIN PracticeArr pa
	ON wd.ArrId = pa.PracticeArrId