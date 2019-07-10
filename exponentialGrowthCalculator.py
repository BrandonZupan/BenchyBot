import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

df = pd.read_csv("userJoinTimes.csv")
df['date'] = pd.to_datetime(df['date'])

dates = df['date']

dates = dates.sort_values()


joinOrder = np.arange(1, dates.size + 1)
dates = dates.to_frame()
dates['joinOrder'] = joinOrder
dates = dates.set_index('joinOrder')

creationdate = dates['date'][1]

dates['serverAge'] = dates['date'] - creationdate
for i in joinOrder:
    age = dates.at[i, 'serverAge'].days + 1
    dates.at[i, 'serverAgeDays'] = age

#Now have a column of each day of each join.  Now to find its equation
x = np.array(dates['serverAgeDays'].values)
y = np.array(joinOrder)
#print(np.where(~np.isfinite(x)))
equation = np.polyfit(x, np.log(y), 1)
print(equation)

a = np.exp(equation[1])
b = equation[0]
print(a, b)

scipyequ = curve_fit(lambda t,a,b: a*np.exp(b*t), x, y, p0=(4, 0.1))
print(scipyequ)

#Graph for pretty
plt.ylabel("Number of Users")
plt.xlabel("Server Age")
plt.plot(x, y)
#ax = plt.axes()
#ax.xaxis.set_major_locator(plt.MaxNLocator(4))

plt.plot(joinOrder, np.exp(0.01*joinOrder), 1000)

plt.savefig("plot.png")



#print(dates)