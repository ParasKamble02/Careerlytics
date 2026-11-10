-- analytical queries 

-- 1. Skill demand: % of postings requiring each skill
SELECT s.skill,
       COUNT(*) AS postings,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs), 1) AS demand_pct
FROM job_skills s
GROUP BY s.skill
ORDER BY postings DESC
LIMIT 15;

-- 2. Role distribution with salary statistics
SELECT role, COUNT(*) AS jobs, ROUND(AVG(salary_lpa), 1) AS avg_lpa, MIN(salary_lpa) AS min_lpa, MAX(salary_lpa) AS max_lpa
FROM jobs GROUP BY role ORDER BY jobs DESC;

-- 3. Top skills for one role
SELECT s.skill, COUNT(*) AS postings
FROM job_skills s JOIN jobs j ON j.job_id = s.job_id
WHERE j.role = 'Data Analyst'
GROUP BY s.skill ORDER BY postings DESC LIMIT 10;

-- 4. Average salary by number of required skills
SELECT n_skills, COUNT(*) AS jobs, ROUND(AVG(salary_lpa), 1) AS avg_lpa
FROM (SELECT j.job_id, j.salary_lpa, COUNT(s.skill) AS n_skills
      FROM jobs j JOIN job_skills s ON s.job_id = j.job_id GROUP BY j.job_id, j.salary_lpa) t
GROUP BY n_skills ORDER BY n_skills;

-- 5. Postings per location
SELECT location, COUNT(*) AS jobs FROM jobs GROUP BY location ORDER BY jobs DESC;
