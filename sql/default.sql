-- Default data for PyStump

-- Default Settings

INSERT OR REPLACE INTO settings(setting_name, setting_value, setting_type) VALUES
       ('Max Duration', 1200, 'number')
       ,('Min Duration', 10, 'number')
       ,('Show Author', 1, 'checkbox')
       ,('Show Updated', 1, 'checkbox')
       ,('Transition Time', 500, 'number')
       ,('Show Title', 1, 'checkbox')
;
