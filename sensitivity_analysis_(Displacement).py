import pandas as pd
import numpy as np
import os 
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.cm as cm

df = pd.read_csv(os.getcwd() + '/' + 'result.csv')
df.head()

for k in range(140,141):
    delta_fos = []
    heading = []
    column_values = []
    var=[ ]

    for i in range(len(df)-1):
        for j in range(1,14):
            if df.iloc[(i+1), (j)] != df.iloc[k,(j)]:
                if ((df.iloc[(i+1), 1:-2]).drop(df.columns[j]) == (df.iloc[k,1:-2]).drop(df.columns[j])).all():
                    delta = round(df.iloc[(i+1), -2] - df.iloc[k,-2],3)
                    delta_fos.append(delta)
                    heading.append(df.columns[j])
                    column_values.append(round(df.iloc[(i+1), -2] - df.iloc[k,-2],3))
                    var.append(df.iloc[(i+1), (j)])
        
    # Create a new DataFrame to store the results
    results_df = pd.DataFrame({
        'Heading': heading,
        'Column_Value': column_values,
        'var': var
    })

    # Group by 'Heading' and aggregate 'Column_Value' and 'var'
    grouped_results_df = results_df.groupby('Heading').agg({
        'Column_Value': list,
        'var': list
    }).reset_index()

    # Transpose the DataFrame
    #transposed_grouped_results_df = grouped_results_df.transpose()

    results_df = grouped_results_df

    print(results_df)


    angle_df = pd.DataFrame(columns=['column_name', 'angle'])
    index = 0
    #plt.figure(figsize=(10,6))

    colors = cm.rainbow(np.linspace(0, 1, len(results_df)))

    for i in range(len(results_df)):  # change this to the actual length of your DataFrame
        x = [0]
        y = [0]
        column_name = results_df.iloc[i,0]
        for j in range(len(results_df.iloc[i,1])):
            x1 = round((results_df.iloc[i,2][j]-df.loc[k,column_name])/df.loc[k,column_name]*100,3)
            y1 = results_df.iloc[i,1][j]
            x.append(x1)
            y.append(y1)

        # If the next data point belongs to a different group, plot the current group and reset x and y
        if i < len(results_df)-1 and results_df.iloc[i,0] != results_df.iloc[i+1,0]:  # change 9 to the actual length of your DataFrame - 1
            slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
            line = slope*np.array(x)+intercept
            plt.plot(x, line, color=colors[i], label=f'{column_name}, angle: {np.round(np.degrees(np.arctan(slope)), 2)} degrees')
            angle_df.loc[index] = [column_name, np.round(np.degrees(np.arctan(slope)), 2)]
            index += 1
            x = []
            y = []

    # Plot the last group
    if x and y:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        line = slope*np.array(x)+intercept
        plt.plot(x, line, color=colors[-1], label=f'{column_name}, angle: {np.round(np.degrees(np.arctan(slope)), 2)} degrees')
        angle_df.loc[index] = [column_name, np.round(np.degrees(np.arctan(slope)), 2)]
    # Add a horizontal and vertical line at 0
    plt.axhline(0, color='black', linewidth=0.5, linestyle='dotted')
    plt.axvline(0, color='black', linewidth=0.5, linestyle='dotted')
    if k == 0:
    # For the first iteration, write the header
        angle_df.to_csv('angles.csv', index=False)

    else:
    # For subsequent iterations, append without writing the header
        angle_df.to_csv('angles.csv', mode='a', header=False, index=False)
    print('Completed Row.No.: ' + str(k))
    # Specify the title and labels
    plt.title('Line plot of delta_fos')
    plt.xlabel('% change')
    plt.ylabel('Delta_FOS')

    # Display the legend
    plt.legend()

    plt.show()