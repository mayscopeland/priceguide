# priceguide
 A Python rewrite of the original fantasy dollar calculator

To use, call the calculate() function, passing it your league settings, the year, and DataFrames of batting and pitching stats. The function returns a new DataFrame with fantasy dollar values and configuration information about your league values (standard deviations, means, and replacement levels).

## Examples

### Standard league values for 2022 stats

```python
import pandas as pd
from priceguide import priceguide

batting_df = pd.read_csv("priceguide/data/2022Batting.csv")
pitching_df = pd.read_csv("priceguide/data/2022Pitching.csv")

values_df, values_config = priceguide.calculate(priceguide.League(), 2022, batting_df, pitching_df)

print(values_df.head())
print(values_config)

values_df.to_csv("MyStandardValues.csv", index=False)
```

### Custom league values

For custom leagues, you can enter your league's settings. You only need to set the properties that are different from a standard 12-team league.

```python
import pandas as pd
from priceguide import priceguide

batting_df = pd.read_csv("priceguide/data/2022Batting.csv")
pitching_df = pd.read_csv("priceguide/data/2022Pitching.csv")

league = priceguide.League()
league.teams = 15
league.budget = 400
league.hitting_categories = ["HR","SB","R","RBI","OBP"]

values_df, values_config = priceguide.calculate(league, 2022, batting_df, pitching_df)

print(values_df.head())
print(values_config)

values_df.to_csv("MyCustomValues.csv", index=False)
```


