import logging
import os
import pickle
from argparse import ArgumentParser
from datetime import datetime
from math import log

from hyperopt import hp, fmin, tpe, space_eval, STATUS_OK, Trials
from hyperopt.mongoexp import MongoTrials
from hyperopt.pyll import scope

from frog import MODEL_TYPES, INPUT_TYPES
from frog.train import train

# {
#     "dropout": 0.21235324691490887,
#     "fc_size": 61.0,
#     "filters_dnb_1": 6,
#     "filters_dnb_2": 0,
#     "filters_dnb_3": 1,
#     "filters_pb_1": 2,
#     "filters_pb_2": 2,
#     "gru_size": 178.0,
#     "inputs": 0,
#     "kernel_size_dnb_1": 2,
#     "kernel_size_dnb_2": 0,
#     "kernel_size_dnb_3": 1,
#     "learning_rate": 0.0037652709773792984,
#     "nade_hidden_size": 460.0,
#     "num_dnb_1": 1,
#     "num_dnb_2": 0,
#     "num_dnb_3": 0,
# }
space = hp.choice(
    "inputs",
    [
        {
            "hyper_params": {
                "conv": {
                    "num_dnb_1": hp.choice("num_dnb_1", [2, 3, 4]),  # 4?
                    "filters_dnb_1": hp.choice("filters_dnb_1", [4, 5, 6, 7, 8, 9, 10]),
                    "bottleneck_filters_dnb_1": 32,  # in the paper this is always 4 * filters_dnb_i
                    "kernel_size_dnb_1": hp.choice("kernel_size_dnb_1", [3, 5, 7]),
                    "filters_pb_1": hp.choice("filters_pb_1", [16, 32, 48]),  # 32?
                    "filters_dnb_2": hp.choice("filters_dnb_2", [4, 5, 6, 7, 8, 9, 10]),
                    "bottleneck_filters_dnb_2": 20,
                    "kernel_size_dnb_2": hp.choice("kernel_size_dnb_2", [3, 5, 7]),
                    "num_dnb_2": hp.choice("num_dnb_2", [2, 3, 4]),  # 2?
                    "filters_pb_2": hp.choice("filters_pb_2", [16, 32, 48]),  # 48?
                    "filters_dnb_3": hp.choice("filters_dnb_3", [4, 5, 6, 7, 8, 9, 10]),
                    "bottleneck_filters_dnb_3": 20,
                    "kernel_size_dnb_3": hp.choice("kernel_size_dnb_3", [3, 5]),
                    "num_dnb_3": hp.choice("num_dnb_3", [2, 3, 4]),  # 2?
                },
                "gru": {
                    "dropout": hp.uniform("dropout", 0.1, 0.4),  # 0.2 seems to be the magic number
                    # "size": 64,
                    "size": scope.int(hp.qloguniform("gru_size", log(8), log(256), 1)),
                },
                "fc": {
                    # "size": 64
                    # This is a bottleneck layer between GRU and NADE, maybe not so useless
                    "size": scope.int(hp.qloguniform("fc_size", log(8), log(256), 1)),
                },
                "nade": {
                    # "hidden_size": 64,
                    "hidden_size": scope.int(
                        hp.qloguniform("nade_hidden_size", log(8), log(512), 1)
                    ),
                    "ensemble_size": 10,
                },
                "optimizer": {
                    # "learning_rate": 0.001,
                    "learning_rate": hp.loguniform(
                        "learning_rate", log(0.0003), log(0.005)
                    ),  # 0.003?
                    "beta_1": 0.9,
                    "beta_2": 0.999,
                    "epsilon": 1e-7,
                    "decay": 0.0,
                },
            }
        }
    ],
)
logger = logging.getLogger(__name__)


def objective(space, args):
    assert args["target"] in ["loss", "RN", "symbols", "both"]
    loss, acc = train(
        args["tfrecords_folder"],
        args["model_folder"],
        args["model_type"],
        space["hyper_params"],
        args["num_epochs"],
        args["batch_size"],
        verbose=False,
    )
    target = args["target"]  # we want to maximise the accuracies, i.e., minimise their negatives
    if target == "loss":
        loss = loss
    elif target == "RN":
        loss = -acc["roman numeral w/ inversion"]
    elif target == "symbols":
        loss = -acc["chord symbol chen and su"]
    elif target == "both":
        loss = -acc["chord symbol chen and su"] - acc["roman numeral w/ inversion"]

    return {"loss": loss, "status": STATUS_OK, "params": space["hyper_params"]}


def main(opts):
    parser = ArgumentParser(description="Search for the best hyperparameter values")
    parser.add_argument(
        "tfrecords_folder",
        help="The folder where the tfrecords generated by the preprocessing module are stored",
    )
    parser.add_argument(
        "-f",
        dest="trials_folder",
        default="../optimisation_trials",
        help="Where to store the optimisation trials. A timestamped subfolder will be created",
    )
    parser.add_argument("-m", dest="model_type", choices=MODEL_TYPES, help="Model to use")
    parser.add_argument("-i", dest="input_type", choices=INPUT_TYPES, help=f"Input type to use")
    parser.add_argument("-n", dest="num_epochs", type=int, default=200, help=f"Epochs per trial")
    parser.add_argument("-t", dest="num_trials", type=int, default=200, help=f"Number of trials")
    parser.add_argument("-b", dest="batch_size", default=128, type=int, help="Batch size")
    parser.add_argument("--mongo_db", help=f"MongoDB ip address for parallelisation")
    parser.add_argument("--experiment_name", help=f"ID for uniquely identifying MongoDB server")
    parser.add_argument("--target", choices=["loss", "RN", "symbols", "both"])

    args = parser.parse_args(opts)

    trials_folder = os.path.join(
        args.trials_folder, f"opt_trial_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    os.makedirs(trials_folder)

    obj_args = {**vars(args), **{"model_folder": trials_folder}}

    def _obj(space):
        return objective(space, obj_args)

    if args.mongo_db is None:
        local = True
        logger.warning("No mongo db ip address found. Running code locally")
        trials = Trials()
    else:
        local = False
        db_ip = f"mongo://{args.mongo_db}:1234/mongo_frog/jobs"
        trials = MongoTrials(db_ip, exp_key=args.experiment_name)

    best = fmin(_obj, space, algo=tpe.suggest, max_evals=args.num_trials, trials=trials)
    print(space_eval(space, best))

    if local:
        with open(os.path.join(trials_folder, "trials.pickle"), "wb") as f:
            pickle.dump(trials, f)
