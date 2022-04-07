# %%
n_estimators = 100
# %%
# Pandas is used for data manipulation
import pandas as pd
from pyparsing import And
# Read in data and display first 5 rows
features = pd.read_csv('IATurnosPredictor.csv')
features.head(5)

# %%
print('The shape of our features is:', features.shape)

# %%
# Descriptive statistics for each column
features.describe()

# %%
# One-hot encode the data using pandas get_dummies
features = pd.get_dummies(features)
# Display the first 5 rows of the last 12 columns
features.iloc[:,5:].head(5)

# %%
# Use numpy to convert to arrays
import numpy as np
# Labels are the values we want to predict
labels = np.array(features['ResultadoEstado'])
# Remove the labels from the features
# axis 1 refers to the columns
features= features.drop('ResultadoEstado', axis = 1)
# Saving feature names for later use
feature_list = list(features.columns)
# Convert to numpy array
features = np.array(features)

# %%
# Using Skicit-learn to split data into training and testing sets
from sklearn.model_selection import train_test_split
# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

# %%
print('Training Features Shape:', train_features.shape)
print('Training Labels Shape:', train_labels.shape)
print('Testing Features Shape:', test_features.shape)
print('Testing Labels Shape:', test_labels.shape)

# %%
# The baseline predictions are the random seed
baseline_preds = test_features[:, feature_list.index('RandomSeed')]
# Baseline errors, and display average baseline error
baseline_errors = abs(baseline_preds - test_labels)
print('RandomSeed baseline error: ', round(np.mean(baseline_errors), 2))

# %%
# Import the model we are using
from sklearn.ensemble import RandomForestRegressor
# Instantiate model with 1000 decision trees
rf = RandomForestRegressor(n_estimators = n_estimators, random_state = 42)
# Train the model on training data
rf.fit(train_features, train_labels);

# %%
# Use the forest's predict method on the test data
predictions = rf.predict(test_features)
# Calculate the absolute errors
errors = abs(predictions - test_labels)
# Print out the mean absolute error (mae)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')

# %%
# Calculate mean absolute percentage error (SMAPE)
smape = 0
for x in range(0, len(predictions), 1):
    if predictions[x] + test_labels[x] != 0:
        smape += ((test_labels[x] + predictions[x])) / (predictions[x])
smape = smape / len(predictions)
accuracy = 100 - np.mean(smape)
print('Accuracy:', round(accuracy, 2), '%.')

# %%
for t in range(0, 11, 1):
    threshold = t / 10
    P = 0
    TP = 0
    N = 0
    TN = 0
    for i in range(0, len(predictions), 1):
        if test_labels[i] == 1:
            P = P + 1
            if predictions[i] >= threshold:
                TP = TP + 1
        if test_labels[i] == 0:
            N = N + 1
            if predictions[i] < threshold:
                TN = TN + 1
    TPR = TP / P
    TNR = TN / N
    FPR = 1 - TNR
    print('Threshold:', threshold)
    print('TPR:', TPR)
    print('FPR:', FPR)
# %%
# Import tools needed for visualization
from sklearn.tree import export_graphviz
import pydot
# Pull out one tree from the forest
tree = rf.estimators_[5]

# %%
# Sanize the labels
import unidecode
for i in range(0, len(feature_list), 1):
    feature_list[i] = unidecode.unidecode(feature_list[i])
# Import tools needed for visualization
from sklearn.tree import export_graphviz
import pydot
# Pull out one tree from the forest
tree = rf.estimators_[5]
# Export the image to a dot file
export_graphviz(tree, out_file = 'tree.dot', feature_names = feature_list, rounded = True, precision = 1)

# %%
# Use dot file to create a graph
(graph, ) = pydot.graph_from_dot_file('tree.dot')

# %%
# Write graph to a png file
graph.write_png('tree.png')

# %%
# Limit depth of tree to 3 levels
rf_small = RandomForestRegressor(n_estimators = 10, max_depth = 3)
rf_small.fit(train_features, train_labels)
# Extract the small tree
tree_small = rf_small.estimators_[5]
# Save the tree as a png image
export_graphviz(tree_small, out_file = 'small_tree.dot', feature_names = feature_list, rounded = True, precision = 1)
(graph, ) = pydot.graph_from_dot_file('small_tree.dot')
graph.write_png('small_tree.png');

# %%
# Get numerical feature importances
importances = list(rf.feature_importances_)
# List of tuples with variable and importance
feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]
# Sort the feature importances by most important first
feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
# Print out the feature and importances 
[print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances];

# %%
# New random forest with only the two most important variables
rf_most_important = RandomForestRegressor(n_estimators= n_estimators, random_state=42)
# Extract the two most important features
important_indices = [feature_list.index('Edad'), feature_list.index('IDTurnosReal')]
train_important = train_features[:, important_indices]
test_important = test_features[:, important_indices]
# Train the random forest
rf_most_important.fit(train_important, train_labels)
# Make predictions and determine the error
predictions = rf_most_important.predict(test_important)
errors = abs(predictions - test_labels)# Display the performance metrics
print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
mape = np.mean(100 * (errors / test_labels))
accuracy = 100 - mape
print('Accuracy:', round(accuracy, 2), '%.')

# %%
# Import matplotlib for plotting and use magic command for Jupyter Notebooks
import matplotlib.pyplot as plt
# %matplotlib inline
# Set the style
plt.style.use('fivethirtyeight')
# list of x locations for plotting
x_values = list(range(len(importances)))
# Make a bar chart
plt.bar(x_values, importances, orientation = 'vertical')
# Tick labels for x axis
plt.xticks(x_values, feature_list, rotation='vertical')
# Axis labels and title
plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances');
# %%
