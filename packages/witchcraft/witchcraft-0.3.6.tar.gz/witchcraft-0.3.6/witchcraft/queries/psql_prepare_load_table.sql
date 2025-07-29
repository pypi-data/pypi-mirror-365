DROP TABLE IF EXISTS data_update;

CREATE TEMP TABLE data_update (
  :(map
     (fn [column]
         (+ (get column 0) " " (get (get column 1) "psql_type")))
    columns),

  PRIMARY KEY (
    :primary_keys
  )
);
