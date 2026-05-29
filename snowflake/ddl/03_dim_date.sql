USE DATABASE SMART_FACTORY_DWH;
USE SCHEMA ANALYTICS;

CREATE OR REPLACE TABLE DIM_DATE (
    DATE_KEY INT PRIMARY KEY, -- Format: YYYYMMDD
    FULL_DATE DATE,
    DAY_OF_WEEK INT,
    DAY_NAME VARCHAR(10),
    DAY_OF_MONTH INT,
    DAY_OF_YEAR INT,
    WEEK_OF_YEAR INT,
    MONTH_NUMBER INT,
    MONTH_NAME VARCHAR(10),
    QUARTER INT,
    YEAR INT,
    IS_WEEKEND BOOLEAN,
    IS_HOLIDAY BOOLEAN DEFAULT FALSE,
    FISCAL_QUARTER INT,
    FISCAL_YEAR INT
);

-- Stored Procedure to populate DIM_DATE
CREATE OR REPLACE PROCEDURE POPULATE_DIM_DATE(START_DATE VARCHAR, END_DATE VARCHAR)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    var start_date = new Date(START_DATE);
    var end_date = new Date(END_DATE);
    
    var currentDate = new Date(start_date.getTime());
    
    while(currentDate <= end_date) {
        var yyyy = currentDate.getFullYear();
        var mm = currentDate.getMonth() + 1;
        var dd = currentDate.getDate();
        
        var dateKey = yyyy * 10000 + mm * 100 + dd;
        var fullDateStr = yyyy + "-" + (mm < 10 ? '0'+mm : mm) + "-" + (dd < 10 ? '0'+dd : dd);
        
        var sql = `
            INSERT INTO DIM_DATE (
                DATE_KEY, FULL_DATE, DAY_OF_WEEK, DAY_NAME, DAY_OF_MONTH, 
                DAY_OF_YEAR, WEEK_OF_YEAR, MONTH_NUMBER, MONTH_NAME, 
                QUARTER, YEAR, IS_WEEKEND, FISCAL_QUARTER, FISCAL_YEAR
            )
            SELECT 
                ${dateKey},
                '${fullDateStr}'::DATE,
                DAYOFWEEKISO('${fullDateStr}'::DATE),
                DAYNAME('${fullDateStr}'::DATE),
                DAYOFMONTH('${fullDateStr}'::DATE),
                DAYOFYEAR('${fullDateStr}'::DATE),
                WEEKISO('${fullDateStr}'::DATE),
                MONTH('${fullDateStr}'::DATE),
                MONTHNAME('${fullDateStr}'::DATE),
                QUARTER('${fullDateStr}'::DATE),
                YEAR('${fullDateStr}'::DATE),
                IFF(DAYOFWEEKISO('${fullDateStr}'::DATE) IN (6, 7), TRUE, FALSE),
                -- Simple fiscal mapping (assuming fiscal year starts in April)
                CASE WHEN MONTH('${fullDateStr}'::DATE) >= 4 THEN QUARTER('${fullDateStr}'::DATE) - 1 ELSE QUARTER('${fullDateStr}'::DATE) + 3 END,
                CASE WHEN MONTH('${fullDateStr}'::DATE) >= 4 THEN YEAR('${fullDateStr}'::DATE) ELSE YEAR('${fullDateStr}'::DATE) - 1 END
            WHERE NOT EXISTS (SELECT 1 FROM DIM_DATE WHERE DATE_KEY = ${dateKey});
        `;
        
        snowflake.execute({sqlText: sql});
        
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return 'DIM_DATE populated successfully.';
$$;

-- Example to run:
-- CALL POPULATE_DIM_DATE('2020-01-01', '2030-12-31');
