algorithms = {
    # Indexing
    1 : {
        # Algorithms attribute
        "name" : "Decision Tree (Classifier)",
        "source" : "Scikit-Learn",
        "type" : "classification",
        "parameters" : {
            # says "param" : ["a", "b", "c"]. "a" be default value for "param". If not, declare the spesifics
            "categorical" : {
                "criterion" : ["gini", "entropy", "log_loss"],
                "splitter" : ["best", "random"],
                "class_weight" : [None, "balanced"], # dict option current not supported
                "max_features" : [None, "sqrt", "log2"], # int, float option current not supported
            },
            "int" : {
                "max_depth" : [None, "int"],
                "max_leaf_nodes" : [None, "int"],
                "min_samples_split" : [2, "int"],
                "min_samples_leaf" : [1, "int"],
                "random_state" : [None, "int"]
            },
            "float" : {
                "min_weight_fraction_leaf" : [0.0, "float"],
                "min_impurity_decrease" : [0.0, "float"]
            },
            "boolean" : {
            }
        }
    },
    2 : {
        "name" : "SVM (LinearSVC)",
        "source" : "Scikit-Learn",
        "type" : "classification",
        "parameters" : {
            "categorical" : {
                "penalty" : ["l2", "l1"],
                "loss" : ['squared_hinge', "hinge"],        
                "multi_class" : ["ovr", "crammer_singer"],
                "dual" : ["auto", "boolean"],
                "class_weight" : [None, "dict", "balanced"],
            },
            "int" : {
                "verbose" : [0, "int"],
                "max_iter" : [1000, "int"],
                "random_state" : [None, "int"]
            },
            "float" : {
                "tol" : [1e-4, "float"],
                "C" : [1.0, "float"],
                "intercept_scaling" : [1.0, "float"],
            },
            "boolean" : {
                "fit_intercept" : [True, False],
            }
        }
    }
}