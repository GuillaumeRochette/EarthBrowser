import csv
import os
import re
import argparse
# Dirty log parser, don't question ...
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse multiple log files into one csv file.")
    parser.add_argument("--log_dir", required=True, help="Path to the directory containing the logs.")
    parser.add_argument("--output", required=True, help="Path of the csv file to be created.")

    args = parser.parse_args()
    log_dir = args.log_dir
    csv_path = args.output
    log_names = sorted(os.listdir(log_dir))
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
    regex_test_accuracy_2 = re.compile('Test net output #4: per_class_accuracy = ([\.\deE+-]+)')

    iterations = []
    train_losses = []
    test_accuracies = []
    test_losses = []
    test_accuracies_0 = []
    test_accuracies_1 = []
    test_accuracies_2 = []
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
        test_accuracy_2 = regex_test_accuracy_2.findall(line)
        if test_accuracy_2:
            test_accuracies_2.append(float(test_accuracy_2[0]))
    with open(csv_path, "w") as csv_file:
        filewriter = csv.writer(csv_file, delimiter=",")
        filewriter.writerow(
            ["Iteration", "Training Loss", "Test Loss", "Test Accuracy", "Class 0 Accuracy", "Class 1 Accuracy",
             "Class 2 Accuracy"])
        for row in zip(iterations, train_losses, test_losses, test_accuracies, test_accuracies_0, test_accuracies_1,
                       test_accuracies_2):
            filewriter.writerow(row)
