from argparse import ArgumentParser
import numpy as np
import tensorflow as tf
import base64
import re

from common import Common
from extractor import Extractor
from config import Config
from interactive_predict import InteractivePredictor
from model import Model

DATA_DIR = "/data/share/ml4se/data/mutation/"
DELIM = " @@ "
file_prefix = DATA_DIR + "java_large_test_create-add-token-replacement"
#file_category = "0"


def get_method(line):
    tokens = line.split(DELIM)
    #name = base64.b64decode(tokens[0]).decode("utf-8")
    body = base64.b64decode(tokens[2]).decode("utf-8")

    return body


def read_file(input_filename):
    with open(input_filename, 'r') as file:
        return [get_method(x) for x in file.readlines()]


def get_lines(input_filename):
    with open(input_filename, 'r') as file:
        return file.readlines()


def eval(true_target_strings, predicted_strings):
    #print(true_target_strings, predicted_strings)
    true_positive, false_positive, false_negative = 0, 0, 0
    true_positive, false_positive, false_negative = model.update_per_subtoken_statistics(
        zip([true_target_strings], [predicted_strings]), true_positive,
        false_positive, false_negative)
    #print(true_positive, false_positive, false_negative)
    precision, recall, f1 = model.calculate_results(true_positive,
                                                    false_positive,
                                                    false_negative)
    return precision, recall, f1


def compare_origin_and_mutation(config, model):
    original_methods = read_file(file_prefix + "original_" + file_category +
                                 ".txt")
    mutated_methods = read_file(file_prefix + "mutated_" + file_category +
                                ".txt")

    n = len(original_methods)
    if len(mutated_methods) != n:
        print("[Error] Two input files have different size.")
        return

    predictor = InteractivePredictor(config, model)

    for i in range(n):
        org_method = original_methods[i]
        mut_method = mutated_methods[i]
        #print(org_method)
        try:
            results = predictor.predict_single_method(org_method + " " +
                                                      mut_method)
        except TimeoutError:
            continue
        org_prediction = [step.prediction for step in results[0].predictions]
        mut_prediction = [step.prediction for step in results[1].predictions]


def predict(config, model):
    methods = read_file(DATA_DIR)

    n = len(methods)

    predictor = InteractivePredictor(config, model)

    fout_add2set = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_add-to-set.txt',
        'w')
    fout_set2add = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_set-to-add.txt',
        'w')

    add2set = 0
    set2add = 0
    i = 0
    for name, method in methods:
        i += 1
        if i % 100 == 0:
            print("predicted %d methods: add2set - %d, set2add - %d" %
                  (i, add2set, set2add))

        if not name.startswith('set') and not name.startswith('add'):
            continue

        #print(org_method)
        try:
            results = predictor.predict_single_method(method)
        except TimeoutError:
            continue

        if len(results) == 0:
            continue
        original_name = results[0].original_name.split(
            Common.internal_delimiter)
        predicted_name = [step.prediction for step in results[0].predictions]
        #print(original_name, predicted_name)

        #org_p, org_r, org_f = eval(original_name, org_prediction)
        #mut_p, mut_r, mut_f = eval(original_name, mut_prediction)

        fout = None
        if original_name[0] == 'set' and predicted_name[0] == 'add':
            fout = fout_set2add
            set2add += 1
        elif original_name[0] == 'add' and predicted_name[0] == 'set':
            fout = fout_add2set
            add2set += 1
        else:
            continue

        fout.write("method name: ")
        for token in original_name:
            fout.write(token + " ")
        fout.write("\nprediction:  ")
        for token in predicted_name:
            fout.write(token + " ")
        fout.write("\n" + method + "\n")

        for timestep, single_timestep_prediction in enumerate(
                results[0].predictions):
            fout.write('Attention:\n')
            fout.write('TIMESTEP: %d\t: %s\n' %
                       (timestep, single_timestep_prediction.prediction))
            for attention_obj in single_timestep_prediction.attention_paths:
                fout.write('%f\tcontext: %s,%s,%s\n' %
                           (attention_obj['score'], attention_obj['token1'],
                            attention_obj['path'], attention_obj['token2']))

        fout.write(
            "======================================================================\n"
        )

        fout_add2set.close()
        fout_set2add.close()

        original_name = results[0].original_name

        org_p, org_r, org_f = eval(original_name, org_prediction)
        mut_p, mut_r, mut_f = eval(original_name, mut_prediction)

        if mut_p < org_p or mut_r < org_r or mut_f < org_f:
            print("method name: \t\t",
                  original_name.split(Common.internal_delimiter))
            print("original prediction: \t", org_prediction)
            print("mutated prediction: \t", mut_prediction, "\n")

            print(org_method)
            print(mut_method)
            print(
                "======================================================================"
            )
        #for index, method_prediction in results.items():
        #    print('Original name:\t%s'% method_prediction.original_name.split('|'))
        #
        #    print('Predicted:\t%s' % [step.prediction for step in method_prediction.predictions])


def predict(config, model):
    methods = read_file(DATA_DIR)

    n = len(methods)

    predictor = InteractivePredictor(config, model)

    fout_add2set = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_add-to-set.txt',
        'w')
    fout_set2add = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_set-to-add.txt',
        'w')

    add2set = 0
    set2add = 0
    i = 0
    for name, method in methods:
        i += 1
        if i % 100 == 0:
            print("predicted %d methods: add2set - %d, set2add - %d" %
                  (i, add2set, set2add))

        if not name.startswith('set') and not name.startswith('add'):
            continue

        #print(org_method)
        try:
            results = predictor.predict_single_method(method)
        except TimeoutError:
            continue

        if len(results) == 0:
            continue
        original_name = results[0].original_name.split(
            Common.internal_delimiter)
        predicted_name = [step.prediction for step in results[0].predictions]
        #print(original_name, predicted_name)

        #org_p, org_r, org_f = eval(original_name, org_prediction)
        #mut_p, mut_r, mut_f = eval(original_name, mut_prediction)

        fout = None
        if original_name[0] == 'set' and predicted_name[0] == 'add':
            fout = fout_set2add
            set2add += 1
        elif original_name[0] == 'add' and predicted_name[0] == 'set':
            fout = fout_add2set
            add2set += 1
        else:
            continue

        fout.write("method name: ")
        for token in original_name:
            fout.write(token + " ")
        fout.write("\nprediction:  ")
        for token in predicted_name:
            fout.write(token + " ")
        fout.write("\n" + method + "\n")

        for timestep, single_timestep_prediction in enumerate(
                results[0].predictions):
            fout.write('Attention:\n')
            fout.write('TIMESTEP: %d\t: %s\n' %
                       (timestep, single_timestep_prediction.prediction))
            for attention_obj in single_timestep_prediction.attention_paths:
                fout.write('%f\tcontext: %s,%s,%s\n' %
                           (attention_obj['score'], attention_obj['token1'],
                            attention_obj['path'], attention_obj['token2']))

        fout.write(
            "======================================================================\n"
        )

    fout_add2set.close()
    fout_set2add.close()


def mutation_flip(config, model):
    original_methods = read_file(file_prefix + "_original.txt")
    mutated_methods = read_file(file_prefix + ".txt")

    n = len(original_methods)
    if len(mutated_methods) != n:
        print("[Error] Two input files have different size.")
        return

    #fout_d_0_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_decrease-0_original.txt")
    #fout_d_0_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_decrease-0.txt")
    #fout_d_1_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_decrease-1_original.txt")
    #fout_d_1_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_decrease-1.txt")
    #fout_i_0_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_increase-0_original.txt")
    #fout_i_0_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_increase-0.txt")
    #fout_i_1_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_increase-1_original.txt")
    #fout_i_1_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_increase-1.txt")
    #fout_same_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_same_original.txt")
    #fout_same_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_same.txt")
    #fout_other_org = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_other_original.txt")
    #fout_other_mut = open("/data/share/ml4se/data/mutation/java_large_test_multi-pass_other.txt")
    d_0 = 0
    d_1 = 0
    i_0 = 0
    i_1 = 0
    same = 0
    other = 0

    predictor = InteractivePredictor(config, model)

    for i in range(n):
        org_method = original_methods[i]
        mut_method = mutated_methods[i]
        #print(org_method)
        try:
            results = predictor.predict_single_method(org_method + " " +
                                                      mut_method)
        except TimeoutError:
            continue
        org_prediction = [step.prediction for step in results[0].predictions]
        mut_prediction = [step.prediction for step in results[1].predictions]

        original_name = results[0].original_name

        org_p, org_r, org_f = eval(original_name, org_prediction)
        mut_p, mut_r, mut_f = eval(original_name, mut_prediction)

        fout_org = None
        fout_mut = None
        if org_prediction == mut_prediction:
            same += 1
        elif original_name == org_prediction and mut_f < 1:
            d_0 += 1
        elif original_name == mut_prediction and org_f < 1:
            i_0 += 1
        elif org_p > mut_p and org_r > mut_r:
            d_1 += 1
        elif org_p < mut_p and org_r < mut_r:
            i_1 += 1
        else:
            other += 1

        print(
            "\rpredicted %d pairs.     d_0: %d, d_1: %d, i_0: %d, i_1: %d, same: %d, other: %d"
            % (i, d_0, d_1, i_0, i_1, same, other),
            end='')

    print("d_0: %d, d_1: %d, i_0: %d, i_1: %d, same: %d, other: %d" %
          (d_0, d_1, i_0, i_1, same, other))


def dic_update(dic, prediction):
    if len(prediction) == 0:
        dic[""] += 1
    else:
        token = prediction[0]
        if token not in dic:
            dic[token] = 1
        else:
            dic[token] += 1


def add_create_predict(config, model):
    original_methods = read_file(file_prefix + "_original.txt")
    mutated_methods = read_file(file_prefix + ".txt")

    n = len(original_methods)

    predictor = InteractivePredictor(config, model)

    fout_create_add2create = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_create_add-to-create_1.txt',
        'w')
    fout_create_create2add = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_create_create-to-add_1.txt',
        'w')
    fout_add_add2create = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_add_add-to-create_1.txt',
        'w')
    fout_add_create2add = open(
        '/data/share/ml4se/example/code2seq_fails/java_large_test_add_create-to-add_1.txt',
        'w')

    tot = 0
    t2t = 0
    t2f = 0
    f2t = 0
    f2f = 0
    create2false = {"": 0}
    add2false = {"": 0}

    for i in range(n):
        org_method = original_methods[i]
        mut_method = mutated_methods[i]

        print(
            "predicted %d methods: tot - %d, t2t - %d, t2f - %d, f2t - %d, f2f - %d"
            % (i, tot, t2t, t2f, f2t, f2f))
        print(create2false)
        print(add2false)

        try:
            results = predictor.predict_single_method(org_method + " " +
                                                      mut_method)
        except TimeoutError:
            continue

        org_prediction = [step.prediction for step in results[0].predictions]
        mut_prediction = [step.prediction for step in results[1].predictions]

        original_name = results[0].original_name.split("|")

        result_org = True if len(org_prediction) > 0 and org_prediction[
            0] == original_name[0] else False
        result_mut = True if len(mut_prediction) > 0 and mut_prediction[
            0] == original_name[0] else False

        #print(original_name, org_prediction, mut_prediction, result_org,
        #      result_mut)
        fout = None
        tot += 1
        if result_org and result_mut:
            t2t += 1
        elif result_org and not result_mut:
            t2f += 1
            if original_name[0] == "create":
                dic_update(create2false, mut_prediction)
                if len(mut_prediction) > 0 and mut_prediction[0] == "add":
                    fout = fout_create_create2add
            else:
                dic_update(add2false, mut_prediction)
                if len(mut_prediction) > 0 and mut_prediction[0] == "create":
                    fout = fout_add_add2create

        elif not result_org and result_mut:
            f2t += 1
            if original_name[0] == "create" and len(
                    mut_prediction) > 0 and mut_prediction[0] == "create":
                fout = fout_create_add2create
            elif original_name[0] == "add" and len(
                    mut_prediction) > 0 and mut_prediction[-1] == "add":
                fout = fout_add_create2add

        else:
            f2f += 1

        if fout == None: continue
        fout.write("method name: ")
        for token in original_name:
            fout.write(token + " ")
        fout.write("\noriginal prediction:  ")
        for token in org_prediction:
            fout.write(token + " ")
        fout.write("\nmutation prediction:  ")
        fout.write("\n[original method]\n" + org_method + "\n[mutation]\n" +
                   mut_method + "\n")

        for timestep, single_timestep_prediction in enumerate(
                results[0].predictions):
            fout.write('Attention:\n')
            fout.write('TIMESTEP: %d\t: %s\n' %
                       (timestep, single_timestep_prediction.prediction))
            for attention_obj in single_timestep_prediction.attention_paths:
                fout.write('%f\tcontext: %s,%s,%s\n' %
                           (attention_obj['score'], attention_obj['token1'],
                            attention_obj['path'], attention_obj['token2']))

        fout.write(
            "======================================================================\n"
        )

    fout_add_add2create.close()
    fout_add_create2add.close()
    fout_create_add2create.close()
    fout_create_create2add.close()
    print("tot - %d, t2t - %d, t2f - %d, f2t - %d, f2f - %d" %
          (tot, t2t, t2f, f2t, f2f))
    print("create2other: ", create2false)
    print("add2other:", add2false)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-d",
                        "--data",
                        dest="data_path",
                        help="path to preprocessed dataset",
                        required=False)
    parser.add_argument("-te",
                        "--test",
                        dest="test_path",
                        help="path to test file",
                        metavar="FILE",
                        required=False)

    parser.add_argument("-s",
                        "--save_prefix",
                        dest="save_path_prefix",
                        help="path to save file",
                        metavar="FILE",
                        required=False)
    parser.add_argument("-l",
                        "--load",
                        dest="load_path",
                        help="path to saved file",
                        metavar="FILE",
                        required=True)
    parser.add_argument(
        '--release',
        action='store_true',
        help=
        'if specified and loading a trained model, release the loaded model for a smaller model '
        'size.')
    parser.add_argument('--predict', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--seed', type=int, default=239)
    args = parser.parse_args()

    np.random.seed(args.seed)
    tf.set_random_seed(args.seed)

    if args.debug:
        config = Config.get_debug_config(args)
    else:
        config = Config.get_default_config(args)

    model = Model(config)
    print('Created model')

    #predict(config, model)
    #mutation_flip(config, model)
    add_create_predict(config, model)
