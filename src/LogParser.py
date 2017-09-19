import re
import csv
import os
import numpy as np

log_dir = "/home/grochette/Documents/SegNet/resources/SegNet5"
log_names = ["caffe.athena-0094.grochette.log.INFO.20170905-172820.11265", "caffe.athena-0094.grochette.log.INFO.20170915-164316.6593"]
lines = []
for log_name in log_names:
    log_path = os.path.join(log_dir, log_name)
    with open(log_path, "r") as log_file:
        for line in log_file:
            lines.append(line)

regex_iteration = re.compile('Iteration (\d+), Testing net')
regex_train_loss = re.compile('Train net output #0: loss = ([\.\deE+-]+)')
regex_test_accuracy = re.compile('Test net output #0: accuracy = ([\.\deE+-]+)')
regex_test_loss = re.compile('Test net output #1: loss = ([\.\deE+-]+)')
regex_test_accuracy_0 = re.compile('Test net output #2: per_class_accuracy = ([\.\deE+-]+)')
regex_test_accuracy_1 = re.compile('Test net output #3: per_class_accuracy = ([\.\deE+-]+)')

iterations = []
train_losses = []
test_accuracies = []
test_losses = []
test_accuracies_0 = []
test_accuracies_1 = []
for line in lines:
    iteration = regex_iteration.findall(line)
    if iteration:
        iterations.append(int(iteration[0]))
    train_loss = regex_train_loss.findall(line)
    if train_loss:
        train_losses.append(float(train_loss[0]))
    test_accuracy = regex_test_accuracy.findall(line)
    if test_accuracy:
        test_accuracies.append(float(test_accuracy[0]))
    test_loss = regex_test_loss.findall(line)
    if test_loss:
        test_losses.append(float(test_loss[0]))
    test_accuracy_0 = regex_test_accuracy_0.findall(line)
    if test_accuracy_0:
        test_accuracies_0.append(float(test_accuracy_0[0]))
    test_accuracy_1 = regex_test_accuracy_1.findall(line)
    if test_accuracy_1:
        test_accuracies_1.append(float(test_accuracy_1[0]))

print iterations
print train_losses
print test_accuracies
print test_losses
print test_accuracies_0
print test_accuracies_1


csv_path = os.path.join(log_dir, "results.csv")
with open(csv_path, "w") as csv_file:
    filewriter = csv.writer(csv_file, delimiter=",")
    filewriter.writerow(["Iteration", "Training Loss", "Test Loss", "Test Accuracy", "Class 0 Accuracy", "Class 1 Accuracy"])
    for row in zip(iterations, train_losses, test_losses, test_accuracies, test_accuracies_0, test_accuracies_1):
        filewriter.writerow(row)