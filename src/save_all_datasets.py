
import pandas as pd
import numpy as np
import sklearn.datasets
from sklearn.preprocessing import QuantileTransformer
import subprocess
from pandas.tseries.offsets import DateOffset
import csv, ast, os

def create_dir_if_needed(iDir):
    try:
        os.makedirs(iDir);
    except:
        pass

# This limit is a "hint" by github. files above 100MB are not allowed.
# No daatset above 100K rows.
# Serious length-based perf tests cannot be performed on these datasets. 
gDatasetLengthLimit = 100000

gTypes = {}

def generate_embedded_dataset(src_filename):
    # src_filename = data/small/adult_small.csv
    (dirname, categ, basename) = src_filename.split("/")
    tgt_filename = dirname + "/embedded_csv/" + basename.replace(".csv", ".i")
    result = subprocess.run(["xxd", "-i", src_filename], capture_output=True)
    lOutput = result.stdout
    # For embedded devices:  'unsigned char' => 'const char'
    lOutput = lOutput.decode()
    lOutput = lOutput.replace("unsigned char ", "const char ")
    with open(tgt_filename, "w") as outfile:
        outfile.write(lOutput)

def array_to_cpp(X, quote = False):
    lQuote = '"' if( quote ) else ""
    result = lQuote + str(X[0]) + lQuote;
    for i in range(1,len(X)):
        if((i % 20) == 0):
            result = result + ",\n\t\t" + lQuote + str(X[i]) + lQuote
        else:
            result = result + ", " + lQuote + str(X[i]) + lQuote
    if(len(X) <= 20):
        result = "{ " + result + " }"
    else:
        result = "{\n\t\t" + result + "\n\t}"        
    return result

def generate_embedded_dataset_parsed(src_filename):
    # src_filename = data/small/adult_small.csv
    (dirname, categ, basename) = src_filename.split("/")
    ds_name = basename.replace(".csv", "")
    tgt_filename = dirname + "/embedded/" + basename.replace(".csv", ".i")
    df = pd.read_csv(src_filename)
    cols = [x for x in df.columns]
    X = df[cols[:-1]].values
    y = df[cols[-1]].values
    (lFeatureType, lTgtType) = gTypes.get(ds_name.split("_")[0], ("float", "double"))
    print("DATASET_FEATURE_TARGET_TYPES", ds_name, ds_name.split("_")[0], (lFeatureType, lTgtType))
    quote_tgt = (lTgtType == "std::string")
    ds_name = ds_name.upper()
    N = df.shape[0]
    with open(tgt_filename, "w") as outfile:
        outfile.write("#include <vector>\n\n")
        outfile.write("using EMBEDDED_FEATURE_TYPE = " + lFeatureType + ";\n")
        outfile.write("using EMBEDDED_TARGET_TYPE = " + lTgtType + ";\n\n")    
        outfile.write("#define EMBEDDED_NB_ROWS " + str(X.shape[0]) + "\n\n")
        outfile.write("#define EMBEDDED_NB_FEATURES " + str(X.shape[1]) + "\n\n")
        outfile.write("using tEmbeddedFeatureVector = EMBEDDED_FEATURE_TYPE[ EMBEDDED_NB_FEATURES ];\n\n")        
        outfile.write("struct sEMBEDDED_X_Y {\n")    
        outfile.write("\ttEmbeddedFeatureVector X;\n")    
        outfile.write("\tEMBEDDED_TARGET_TYPE y;\n};\n\n")    
        X_output = "static const std::vector<sEMBEDDED_X_Y> gEMBEDDED_DATASET {\n"
        outfile.write(X_output)    
        for row in range(N):
            y_i = str(y[row])
            if(quote_tgt):
                y_i = '"' +  y_i + '"'
            X_output = "\t{ .X = " + array_to_cpp(X[row, :]) + ", .y = " + y_i + " }"
            if((row +1) < N):
                X_output = X_output + ",\n"
            else:
                X_output = X_output + "\n"
                
            outfile.write(X_output)    
        outfile.write("}; // eof gEMBEDDED_DATASET\n")    

def quantize_column(X):
    qt = QuantileTransformer(n_quantiles=10, random_state=0)
    X_qt = qt.fit_transform(X.reshape(-1, 1))
    # print(X_qt.dtype)
    X_qt[np.isnan(X_qt)] = 0.5 # median-based missing imputation.
    X_qt = X_qt.round(3)
    X_qt = X_qt * 10
    X_qt = X_qt.astype(int)
    return X_qt.reshape(-1, 1)


def save_raw(ds_name, X, y, feature_names):
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y
    df = df.head(gDatasetLengthLimit);
    print("RAW_DATA_EXTRACT_START", ds_name)
    df.info()
    print(df.head())
    print("RAW_DATA_EXTRACT_END", ds_name)
    df.to_csv("data/raw/" + ds_name + "_raw.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);    

def save_artificial_missing(ds_name, X, y, feature_names):
    rng = np.random.default_rng(seed=1789)
    if(hasattr(X, "values")):
        X1 = X.values.copy()
    else :
        X1 = X.copy()
    df = pd.DataFrame(X1, columns=feature_names)
    df = df.head(gDatasetLengthLimit);
    
    for c in df.columns:
        print("save_artificial_missing" , (ds_name, c))
        df[c] = df[c].apply(lambda x : x if(rng.uniform() > 0.05) else None)
    df["target"] = y[:gDatasetLengthLimit]
    df.info()
    df.to_csv("data/missing/" + ds_name + "_missing.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);    


def save_dataset_flavors(ds_name, X, y, feature_names, sample_medium = False):
    print("SAVE_DATASET_FLAVORS", ds_name, X.shape, y.shape, type(X))
    X_qt = X.copy()
    if(pd.core.frame.DataFrame == type(X)):
        for col in X.columns:
            if((X[col].dtype != object) and (X[col].dtype.name != "str")):
                X_qt[col] = quantize_column(X[col].values).flatten()
        df = X
    else:
        for j in range(X.shape[1]):
            X_qt[:, j] = quantize_column(X[:, j]).flatten()
        df = pd.DataFrame(X , columns = feature_names)                
    df = df.fillna(0)
    df["target"] = y
    df.info()
    df = df.head(gDatasetLengthLimit)
    df.to_csv("data/original/" + ds_name + ".csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    df_small = df.sample(n=64, random_state=1789)
    df_small.info()
    df_small.to_csv("data/small/" + ds_name + "_small.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    df_tiny = df.sample(n=16, random_state=1789)
    df_tiny.info()
    df_tiny.to_csv("data/tiny/" + ds_name + "_tiny.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    if(sample_medium):
        df_medium = df.sample(n=512, random_state=1789)
        df_medium.info()
        df_medium.to_csv("data/medium/" + ds_name + "_medium.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    else:
        df_medium = df.head(512)
        df_medium.info()
        df_medium.to_csv("data/medium/" + ds_name + "_medium.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);

    df_sampled = df.sample(n=df.shape[0] // 8, random_state=1789)
    df_sampled.info()
    df_sampled.to_csv("data/sampled/" + ds_name + "_sampled.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
        
    df_qt = pd.DataFrame(X_qt , columns = feature_names)
    df_qt["target"] = y
    df_qt.info()
    df_qt = df_qt.head(gDatasetLengthLimit)
    df_qt.to_csv("data/quantized/" + ds_name + "_quantized.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);

    generate_embedded_dataset("data/small/" + ds_name + "_small.csv");
    generate_embedded_dataset("data/tiny/" + ds_name + "_tiny.csv");
    generate_embedded_dataset("data/medium/" + ds_name + "_medium.csv");
    if(X.shape[0] < 5120):
        generate_embedded_dataset("data/original/" + ds_name + ".csv"); #  too large ??

    generate_embedded_dataset_parsed("data/small/" + ds_name + "_small.csv");
    generate_embedded_dataset_parsed("data/tiny/" + ds_name + "_tiny.csv");
    generate_embedded_dataset_parsed("data/medium/" + ds_name + "_medium.csv");
    if(X.shape[0] < 5120):
        generate_embedded_dataset_parsed("data/original/" + ds_name + ".csv"); #  too large ??

def save_raw_dataset_flavors(ds_name, X, y, feature_names):
    print("SAVE_RAW_DATASET_FLAVORS", ds_name, X.shape, y.shape, type(X))
    if(pd.core.frame.DataFrame == type(X)):
        df = X
    else:
        df = pd.DataFrame(X , columns = feature_names)                
    df["target"] = y
    df.info()
    df = df.head(gDatasetLengthLimit)
    df.to_csv("data/original/" + ds_name + ".csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    
    df_small = df.sample(n=64, random_state=1789)
    df_small.info()
    df_small.to_csv("data/small/" + ds_name + "_small.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    df_tiny = df.sample(n=16, random_state=1789)
    df_tiny.info()
    df_tiny.to_csv("data/tiny/" + ds_name + "_tiny.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    df_medium = df.sample(n=512, random_state=1789)
    df_medium.info()
    df_medium.to_csv("data/medium/" + ds_name + "_medium.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    df_sampled = df.sample(n=df.shape[0] // 8, random_state=1789)
    df_sampled.info()
    df_sampled.to_csv("data/sampled/" + ds_name + "_sampled.csv", index= False, quoting=csv.QUOTE_NONNUMERIC);
    
def save_titanic():
    from sklearn import datasets
    titanic = datasets.fetch_openml(name='titanic', version=1)
    X = titanic.data.values
    y = titanic.target.values
    feature_names = titanic.feature_names
    gTypes["titanic"] = ("float", "std::int32_t")
    save_raw("titanic", X, y, feature_names)
    save_artificial_missing("titanic", X, y, feature_names)
    save_raw_dataset_flavors("titanic", X, y, feature_names)

def save_iris_quantized():
    from sklearn.datasets import load_iris
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    gTypes["iris"] = ("float", "std::int32_t")
    save_raw("iris", X, y, feature_names)
    save_artificial_missing("iris", X, y, feature_names)
    save_dataset_flavors("iris", X, y, feature_names)

def save_digits_quantized():
    from sklearn.datasets import load_digits
    digits = load_digits()
    X = digits.data
    y = digits.target
    X = X.astype(np.int8)
    gTypes["digits"] = ("std::int8_t", "std::int32_t")

    feature_names = digits.feature_names

    save_raw("digits", X, y, feature_names)
    save_artificial_missing("digits", X, y, feature_names)
    save_dataset_flavors("digits", X, y, feature_names)


def save_census_quantized():
    from sklearn.datasets import fetch_openml
    gTypes["census"] = ("float", "std::string")
    census = fetch_openml(name="adult", version=2)
    X = census.data
    y = census.target
    X1 = X.copy();
    print(X1.columns)
    non_numerical_cols = ["workclass", "education","marital-status","occupation","relationship","race","sex", "native-country"]
    for col in non_numerical_cols:
        X1[col] = 0.0;
    print(X1.values)
    for col in X1.columns:
        X1[col] = X1[col].astype(float)
    X1.info()
    print(X1.values)

    feature_names = census.feature_names
    save_dataset_flavors("census", X1, y, feature_names)

def encode_one_hot(df, categorical_cols):
    from sklearn.preprocessing import OneHotEncoder
    df_hot = pd.DataFrame();
    for col in df.columns:
        if(col in categorical_cols):
            X1 = df[col].values.reshape(-1, 1)
            X1 = np.ascontiguousarray(X1)
            enc = OneHotEncoder(handle_unknown='ignore', sparse_output=False, drop='if_binary', min_frequency=5, max_categories=7)
            X2 = enc.fit_transform(X1);                
            feature_names_col = enc.get_feature_names_out()
            print(col, feature_names_col)
            for c in range(X2.shape[1]):
                name = feature_names_col[c]
                name = name.replace("x0_", col + "_")
                df_hot[name] = X2[:,c]
        else:
            df_hot[col] = df[col]
    print(df_hot)
    return df_hot
    
def save_census_one_hot():
    from sklearn.datasets import fetch_openml
    gTypes["census"] = ("float", "std::string")
    census = fetch_openml(name="adult", version=2)
    y = census.target
    X = census.data
    save_raw("census", X.values, y.values, census.feature_names)
    save_artificial_missing("census", X, y, census.feature_names)
    non_numerical_cols = ["workclass", "education","marital-status","occupation","relationship","race","sex", "native-country"]
    X_hot = encode_one_hot(X, non_numerical_cols)
    feature_names = X_hot.columns
    print(feature_names)
    save_raw("census_one_hot", X_hot.values, y, feature_names)
    save_artificial_missing("census_one_hot", X_hot.values, y, feature_names)
    save_dataset_flavors("census_one_hot", X_hot.values, y, feature_names)

def save_raw_census():
    from sklearn.datasets import fetch_openml
    gTypes["adult"] = ("float", "std::string")
    census = fetch_openml(name="adult", version=2)
    y = census.target
    X = census.data
    feature_names = census.feature_names
    print(feature_names)
    save_raw("adult", X, y, feature_names)
    save_artificial_missing("adult", X, y, feature_names)
    save_raw_dataset_flavors("adult", X, y, feature_names)

def save_hotel_reviews():
    from sklearn.datasets import fetch_openml
    gTypes["adult"] = ("float", "std::string")
    ds_name = "hotel_reviews"
    hotel_reviews = fetch_openml(name="515K-Hotel-Reviews-Data-in-Europe", version=1)
    feature_names = [x  for x in hotel_reviews.feature_names if(x != "Reviewer_Score")]    
    y = hotel_reviews.data["Reviewer_Score"].values
    X = hotel_reviews.data[feature_names].values
    tags = hotel_reviews.data["Tags"].values.tolist()
    tags_dict = {}
    for (i, tag_list) in enumerate(tags):
        lList = ast.literal_eval(tag_list)
        for tag in lList:
            tag1 = tag.strip().replace(" ", "_")
            # tag1 = "_".join(tag1.split("_")[:3])
            tags_dict[tag1] = tags_dict.get(tag1, {})
            tags_dict[tag1][i] = 1
    freq_tags_sorted = sorted([(tag, v) for (tag,v) in tags_dict.items()], key = lambda x : -len(x[1]))[:64]
    freq_tags = [tag for (tag, v) in freq_tags_sorted]
    print(freq_tags)
    df = pd.DataFrame(X, columns=feature_names)
    N = X.shape[0]
    for tag in freq_tags:
        v = tags_dict[tag]
        list_tag = [0]*N
        for i in v:
            list_tag[i] = 1
        df["Tag_" + tag] = list_tag
    feature_names = [x  for x in df.columns if(x != "Tags")]    
    y = hotel_reviews.data["Reviewer_Score"]
    X = df[feature_names].values
    print(feature_names)
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_raw_dataset_flavors(ds_name, X, y, feature_names)


def save_kdd_1999():
    gTypes["kdd_1999"] = ("float", "std::string")
    feature_names = "duration protocol_type service flag src_bytes dst_bytes land wrong_fragment urgent hot num_failed_logins logged_in num_compromised root_shell su_attempted num_root num_file_creations num_shells num_access_files num_outbound_cmds is_host_login is_guest_login count srv_count serror_rate srv_serror_rate rerror_rate srv_rerror_rate same_srv_rate diff_srv_rate srv_diff_host_rate dst_host_count dst_host_srv_count dst_host_same_srv_rate dst_host_diff_srv_rate dst_host_same_src_port_rate dst_host_srv_diff_host_rate dst_host_serror_rate dst_host_srv_serror_rate dst_host_rerror_rate dst_host_srv_rerror_rate".split(" ")    
    categorical_cols = ["protocol_type", "service", "flag", "intrusion_category"]
    float_cols = [x for x in feature_names if x.endswith("_rate")]
    int_cols = [x for x in feature_names if x.endswith("_bytes")] 
    large_cols = categorical_cols + float_cols + int_cols
    int8_cols = [x for x in feature_names if x not in large_cols]
    dtypes = dict([(x , "category") for x in categorical_cols] +
                  [(x , "int32") for x in int_cols] +
                  [(x , "float32") for x in float_cols] +
                  [(x , "int8") for x in int8_cols])
    df = pd.read_csv("source_data/kddcup_1999/kddcup_1999_normalized.csv.gz", dtype=dtypes)
    print(df.columns)
    df_hot = encode_one_hot(df, categorical_cols[:-1])
    df_hot.info()
    feature_names = df_hot.columns[:-1]
    X = df_hot[feature_names].values.astype(np.float32)
    X = X.round(4)    
    y = df_hot["intrusion_category"].str.replace('.','')
    y = y.values
    save_dataset_flavors("kddcup_1999", X, y, feature_names)


def save_kdd_2009():
    gTypes["kdd_2099"] = ("float", "int")
    df_X = pd.read_csv("source_data/kddcup_2009/orange_small_train.data", sep="\t")
    df_y = pd.read_csv("source_data/kddcup_2009/orange_small_train_churn.labels", header=None)    
    print(df_X.columns)
    ds_name = "kdd_2009"
    feature_names = df_X.columns
    X = df_X.values
    y = df_y.values
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    categorical_cols = [col for col in df_X.columns if (df_X[col].dtype == object or df_X[col].dtype.name == "str")]
    print(categorical_cols)
    df_hot = encode_one_hot(df_X, categorical_cols)
    df_hot.info()
    print(df_hot.columns)
    feature_names = df_hot.columns[:-1]
    X = df_hot[feature_names].values.astype(np.float32)
    X = X.round(4)    
    y = df_y[0].values
    save_dataset_flavors("kddcup_2009", X, y, feature_names)

def save_mushroom():
    from sklearn.datasets import fetch_openml
    gTypes["mushroom"] = ("float", "std::string")
    mushroom = fetch_openml(name="mushroom")
    feature_names = mushroom.feature_names
    X = mushroom.data
    y = mushroom.target # tartget = "class", 2 categories 'e' (edible) and 'p' (poisonous).
    ds_name = "mushroom"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    categorical_cols = feature_names # all 22 features are categorical
    df_hot = encode_one_hot(X, categorical_cols)
    df_hot.info()
    print(df_hot.columns)
    X = df_hot.values.astype(np.float32)
    X = X.round(4)    
    save_dataset_flavors("mushroom", X, y, df_hot.columns)

def save_glass():
    from sklearn.datasets import fetch_openml
    gTypes["glass"] = ("float", "std::string")
    glass = fetch_openml(name="glass")
    feature_names = glass.feature_names
    X = glass.data
    y = glass.target # 
    ds_name = "glass"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    categorical_cols = [] # none
    df_hot = encode_one_hot(X, categorical_cols)
    df_hot.info()
    print(df_hot.columns)
    X = df_hot.values.astype(np.float32)
    X = X.round(4)    
    save_dataset_flavors("glass", X, y, df_hot.columns)

def save_spambase():
    from sklearn.datasets import fetch_openml
    gTypes["spambase"] = ("float", "int")
    spambase = fetch_openml(name="spambase")
    feature_names = spambase.feature_names
    X = spambase.data
    y = spambase.target # 
    ds_name = "spambase"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    categorical_cols = [] # none
    df_hot = encode_one_hot(X, categorical_cols)
    df_hot.info()
    print(df_hot.columns)
    X = df_hot.values.astype(np.float32)
    X = X.round(4)    
    save_dataset_flavors("spambase", X, y, df_hot.columns, sample_medium = True)

    
def save_abalone():
    gTypes["abalone"] = ("float", "float")
    from sklearn.datasets import fetch_openml
    abalone = fetch_openml(name="abalone")
    feature_names = abalone.feature_names
    X = abalone.data
    y = abalone.target # tartget = "class", 2 categories 'e' (edible) and 'p' (poisonous).
    ds_name = "abalone"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    categorical_cols = [ 'Sex' ] 
    df_hot = encode_one_hot(X, categorical_cols)
    df_hot.info()
    print(df_hot.columns)
    X = df_hot.values.astype(np.float32)
    X = X.round(4)
    save_dataset_flavors("abalone", X, y, df_hot.columns)

    
def save_california_housing_quantized():
    from sklearn.datasets import fetch_openml
    california_housing = fetch_openml(name="california_housing")
    X = california_housing.data
    y = california_housing.target
    ds_name = "california_housing"
    feature_names = california_housing.feature_names
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)

    print(X.columns)
    X1 = X.copy();
    print(X1.columns)
    non_numerical_cols = ["ocean_proximity"]
    for col in non_numerical_cols:
        X1[col] = 0.0;
    print(X1.values)
    for col in X1.columns:
        X1[col] = X1[col].astype(float)
    X1.info()
    print(X1.values)
    gTypes["california_housing"] = ("float", "double")
    
    save_dataset_flavors("california_housing", X1, y, feature_names)

    
def save_diabetes_quantized():
    from sklearn.datasets import load_diabetes
    diabetes = load_diabetes()
    X = diabetes.data
    y = diabetes.target
    feature_names = diabetes.feature_names
    gTypes["diabetes"] = ("float", "double")
    ds_name = "diabetes"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_dataset_flavors("diabetes", X, y, feature_names)

def save_hard_task_classification_dataset():
    NF = 32
    for NC in [16, 32, 64]:
        (X, y) = sklearn.datasets.make_classification(
            n_samples=8192, n_classes=NC, n_features=NF, n_informative=NF//2, random_state=1789);
        X = X.round(2)
        feature_names = ["X_" + str(i) for i in range(X.shape[1])]
        ds_name = "many_classes_dataset_" + str(NC)
        save_raw(ds_name, X, y, feature_names)
        save_artificial_missing(ds_name, X, y, feature_names)
        gTypes[ds_name] = ("float", "double")
        save_dataset_flavors(ds_name, X, y, feature_names)

def save_easy_task_classification_dataset():
    NF = 32
    NC = 4
    (X, y) = sklearn.datasets.make_classification(
        n_samples=8192, n_classes=NC, n_features=NF, n_informative=NF//2, random_state=1789);
    X = X.round(2)
    y1 = X.mean(axis = 1).reshape(-1)
    print(y1.shape)
    y1 = np.round(y1).astype(int)
    y1 = np.remainder(y1, NC)
    feature_names = ["X_" + str(i) for i in range(X.shape[1])]
    ds_name = "easy_class_task_linear_" + str(NC)
    gTypes[ds_name] = ("float", "int")
    save_raw(ds_name, X, y1, feature_names)
    save_artificial_missing(ds_name, X, y1, feature_names)
    save_dataset_flavors(ds_name, X, y1, feature_names)

def save_64_1024_features_classification_dataset():
    for NF in [64, 128, 256, 512, 1024]:
        (X, y) = sklearn.datasets.make_classification(
            n_samples=8192, n_classes=16, n_features=NF, n_informative=NF//2, random_state=1789);
        X = X.round(2)
        feature_names = ["X_" + str(i) for i in range(X.shape[1])]
        ds_name = str(NF) + "_features_16_classes"
        gTypes[ds_name] = ("float", "double")
        save_raw(ds_name, X, y, feature_names)
        save_artificial_missing(ds_name, X, y, feature_names)
        save_dataset_flavors(ds_name, X, y, feature_names)

    
def save_64_1024_features_regression_dataset():
    for NF in [64, 128, 256, 512, 1024]:
        (X, y) = sklearn.datasets.make_regression(n_samples=8192, n_features=NF, n_informative=NF//2, random_state=1789);
        X = X.round(2)
        y = y.round(2)
        feature_names = ["X_" + str(i) for i in range(X.shape[1])]
        ds_name = str(NF) + "_features_reg"
        gTypes[ds_name] = ("float", "double")
        save_raw(ds_name, X, y, feature_names)
        save_artificial_missing(ds_name, X, y, feature_names)
        save_dataset_flavors(ds_name, X, y, feature_names)

def save_easy_task_regression_dataset():
    NF = 12
    (X, y) = sklearn.datasets.make_regression(n_samples=8192, n_features=NF, n_informative=NF//2, random_state=1789);
    X = X.round(2)
    y1 = X.mean(axis = 1)
    feature_names = ["X_" + str(i) for i in range(X.shape[1])]
    ds_name = "easy_reg_task_linear"
    gTypes[ds_name] = ("float", "float")
    save_raw(ds_name, X, y1, feature_names)
    save_artificial_missing(ds_name, X, y1, feature_names)
    save_dataset_flavors(ds_name, X, y1, feature_names)
    y2 = 0.0 * y1
    ds_name = "easy_reg_task_zero"
    gTypes[ds_name] = ("float", "float")
    save_raw(ds_name, X, y2, feature_names)
    save_artificial_missing(ds_name, X, y2, feature_names)
    save_dataset_flavors(ds_name, X, y2, feature_names)
    y3 = y2 + 3.14
    ds_name = "easy_reg_task_const_pi"
    gTypes[ds_name] = ("float", "float")
    save_raw(ds_name, X, y3, feature_names)
    save_artificial_missing(ds_name, X, y3, feature_names)
    save_dataset_flavors(ds_name, X, y3, feature_names)

# white noise prediction
def save_hard_task_regression_dataset():
    NF = 12
    (X, y) = sklearn.datasets.make_regression(n_samples=8192, n_features=NF, n_informative=NF//2, random_state=1789);
    X = X.round(2)
    feature_names = ["X_" + str(i) for i in range(X.shape[1])]
    mu, sigma = 0.0, 1.0
    rng = np.random.default_rng(seed = 1789)
    y = rng.normal(mu, sigma, 8192)
    ds_name = "hard_reg_task_white_noise_Normal_0_1"
    gTypes[ds_name] = ("float", "float")
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_dataset_flavors(ds_name, X, y, feature_names)
    
def save_friedman_robot_arm(iSeed = 1789):
    # http://www.milbo.users.sonic.net/earth/Friedman-FastMars.pdf
    # http://www.milbo.users.sonic.net/earth/earth-times.html
    rng = np.random.default_rng(seed=iSeed)
    ncases = 3000
    l1 = rng.random((ncases,))
    l2 = rng.random((ncases,))
    theta1 = 2*np.pi * rng.random((ncases,))
    theta2 = 2*np.pi * rng.random((ncases,))
    phi = np.pi * rng.random((ncases,)) - np.pi/2
    X = np.vstack((l1, l2, theta1, theta2, phi))
    X = X.transpose()
    for i in range(25): # 25 dummy vars, so 30 vars in total
        u = rng.random((ncases,)).reshape(-1, 1)
        X = np.hstack((X, u))
    feature_names = ["l1", "l2", "theta1", "theta2", "phi"] + ["Noise_" + str(i) for i in range(25)]
    
    robot_x = l1 * np.cos(theta1) - l2 * np.cos(theta1 + theta2) * np.cos(phi)
    robot_y = l1 * np.sin(theta1) - l2 * np.sin(theta1 + theta2) * np.cos(phi)
    robot_z = l2 * np.sin(theta2) * np.sin(phi)
    robot_d = np.sqrt(robot_x*robot_x + robot_y*robot_y + robot_z*robot_z)
    y = robot_d
    X = X.astype(np.float32)
    X = X.round(4)
    y = y.astype(np.float32)
    y = y.round(4)
    save_raw("friedman_robot_arm", X, y, feature_names)
    save_artificial_missing("friedman_robot_arm", X, y, feature_names)
    gTypes["friedman_robot_arm"] = ("float", "float")    
    save_dataset_flavors("friedman_robot_arm", X, y, feature_names)

def save_earth_ozone1():
    df = pd.read_csv("source_data/earth_ozone1.csv")
    print(df.columns)
    X = df.values[:,2:]
    y = df.values[:,1]
    X = X.astype(np.float32)
    X = X.round(4)
    y = y.astype(np.float32)
    y = y.round(4)
    feature_names = df.columns[2:]
    save_raw("earth_ozone1", X, y, feature_names)
    save_artificial_missing("earth_ozone1", X, y, feature_names)
    gTypes["earth_ozone1"] = ("float", "float")    
    save_dataset_flavors("earth_ozone1", X, y, feature_names)
    
def save_age_dataset():
    # source : https://github.com/Moradnejad/AgeDataset
    gTypes["age_dataset"] = ("float", "float")    
    df = pd.read_csv("source_data/AgeDataset.csv.gz")
    print(df.columns)
    X = df[df.columns[:-1]].values
    y = df[df.columns[-1]].values
    save_raw("age_dataset", X, y, df.columns[:-1])
    save_artificial_missing("age_dataset", X, y, df.columns[:-1])
    non_numerical_cols = [col for col in df.columns if (df[col].dtype==object) or (df[col].dtype.name=="str")]
    X_hot = encode_one_hot(df, non_numerical_cols)
    feature_names = X_hot.columns
    print(feature_names)
    y = df[df.columns[-1]]
    save_dataset_flavors("age_dataset", X_hot, y, feature_names)
    

gRegressionDatasets = {}
gClassificationDatasets = {}
gClassificationDatasets["BreastCancer"] = sklearn.datasets.load_breast_cancer();
gClassificationDatasets["BinaryClass_10"] = sklearn.datasets.make_classification(
    n_samples=1024, n_classes=2, n_features=10, random_state=1789);
gClassificationDatasets["FourClass_10"] = sklearn.datasets.make_classification(
    n_samples=1024, n_classes=4, n_features=10, n_informative=4, random_state=1789);
gClassificationDatasets["BinaryClass_100"] = sklearn.datasets.make_classification(
    n_samples=1024, n_classes=2, n_features=100, random_state=1789);
gClassificationDatasets["FourClass_100"] = sklearn.datasets.make_classification(
    n_samples=1024, n_classes=4, n_informative=10, n_features=100, random_state=1789);
    
gRegressionDatasets["friedman1"] = sklearn.datasets.make_friedman1(random_state=1789)
gRegressionDatasets["friedman2"] = sklearn.datasets.make_friedman2(random_state=1789)
gRegressionDatasets["friedman3"] = sklearn.datasets.make_friedman3(random_state=1789)
gRegressionDatasets["RandomReg_10"] = sklearn.datasets.make_regression(n_samples=1024, n_features=10, random_state=1789);
gRegressionDatasets["RandomReg_100"] = sklearn.datasets.make_regression(n_samples=1024, n_features=100, random_state=1789);

def save_class_generated_dataset_quantized(ds_name):
    lDataset = gClassificationDatasets[ds_name]
    if(type(lDataset) == tuple):
        (X, y) = lDataset
        feature_names = ["X_" + str(i) for i in range(X.shape[1])]
    else:
        X = lDataset.data
        y = lDataset.target
        feature_names = lDataset.feature_names

    gTypes[ds_name.split("_")[0]] = ("float", "std::int32_t")
    if(y.dtype == "np.int64"):
        gTypes[ds_name.split("_")[0]] = ("float", "std::int32_t")

    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_dataset_flavors(ds_name, X, y, feature_names)

def save_reg_generated_dataset_quantized(ds_name):
    lDataset = gRegressionDatasets[ds_name]
    if(type(lDataset) == tuple):
        (X, y) = lDataset
        feature_names = ["X_" + str(i) for i in range(X.shape[1])]
    else:
        X = lDataset.data
        y = lDataset.target
        feature_names = lDataset.feature_names

    gTypes[ds_name.split("_")[0]] = ("float", "float")

    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_dataset_flavors(ds_name, X, y, feature_names)


def save_generated_datetimes_class():
    NF = 24
    (X, y) = sklearn.datasets.make_classification(
        n_samples=8192, n_classes=4, n_features=NF, n_informative=NF//2, random_state=1789);
    X = X.round(2)
    df = pd.DataFrame(X)
    df.columns = ['X_' + str(i) for i in range(NF)]
    NR = df.shape[0]
    df['h'] = np.random.randint(12, size=NR)
    df['d'] = np.random.randint(6, size=NR) + 6
    df['m'] = np.random.randint(30, size=NR)
    df['purchase_date'] = pd.date_range(start="05/07/2001", periods=X.shape[0], freq='D')
    df['purchase_date'] = df['purchase_date'].sample(frac=1)
    df['return_date'] = df[['purchase_date', 'm' , 'h', 'd']].apply(
        lambda x : x["purchase_date"] + DateOffset(months=x["m"], hours=x["h"], days=x["d"]), axis=1)
    df["target"] = df["h"] + df["m"] + df["d"]
    df['h'] = df['h'].apply(lambda x : 'h_' + str(x))
    df['h'] = df['m'].apply(lambda x : 'm_' + str(x))
    df['h'] = df['d'].apply(lambda x : 'd_' + str(x))
    df["target"] = df["target"].mod(4)
    cols = [x for x in df.columns]
    (X, y) = (df[cols[:-1]].values, df[cols[-1]].values)
    feature_names = cols[:-1]
    ds_name = "repair_dates_4_class"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_raw_dataset_flavors(ds_name, X, y, feature_names)


def save_generated_datetimes_reg():
    NF = 24
    (X, y) = sklearn.datasets.make_regression(
        n_samples=8192, n_features=NF, n_informative=NF//2, random_state=1789);
    X = X.round(2)
    df = pd.DataFrame(X)
    df.columns = ['X_' + str(i) for i in range(NF)]
    NR = df.shape[0]
    df['h'] = np.random.randint(12, size=NR)
    df['d'] = np.random.randint(6, size=NR) + 6
    df['m'] = np.random.randint(30, size=NR)
    df['purchase_date'] = pd.date_range(start="12/06/2001", periods=X.shape[0], freq='D')
    df['purchase_date'] = df['purchase_date'].sample(frac=1)
    df['return_date'] = df[['purchase_date', 'm' , 'h', 'd']].apply(
        lambda x : x["purchase_date"] + DateOffset(months=x["m"], hours=x["h"], days=x["d"]), axis=1)
    df["target"] = df["h"] + df["m"] + df["d"]
    df['h'] = df['h'].apply(lambda x : 'h_' + str(x))
    df['m'] = df['m'].apply(lambda x : 'm_' + str(x))
    df['d'] = df['d'].apply(lambda x : 'd_' + str(x))
    cols = [x for x in df.columns]
    (X, y) = (df[cols[:-1]].values, df[cols[-1]].values)
    feature_names = cols[:-1]
    ds_name = "repair_dates_4_reg"
    save_raw(ds_name, X, y, feature_names)
    save_artificial_missing(ds_name, X, y, feature_names)
    save_raw_dataset_flavors(ds_name, X, y, feature_names)



def save_all_classification_datasets():
    save_kdd_2009()
    save_iris_quantized()
    save_titanic()
    save_digits_quantized()
    save_census_quantized()
    save_census_one_hot()
    save_64_1024_features_classification_dataset()
    save_generated_datetimes_class()
    save_generated_datetimes_reg()
    save_easy_task_classification_dataset()
    save_hard_task_classification_dataset()
    for ds_name in gClassificationDatasets.keys():
        save_class_generated_dataset_quantized(ds_name)
    save_kdd_1999()
    save_mushroom()
    save_glass()
    save_spambase()
    save_raw_census()
    save_hotel_reviews()


def save_all_regression_datasets():
    save_california_housing_quantized()
    save_diabetes_quantized()
    save_64_1024_features_regression_dataset()
    save_easy_task_regression_dataset()
    save_hard_task_regression_dataset()
    save_friedman_robot_arm()
    save_earth_ozone1()
    for ds_name in gRegressionDatasets.keys():
        save_reg_generated_dataset_quantized(ds_name)
    save_abalone()
    save_age_dataset()

def create_all_dirs_if_needed():
    dirs = "embedded medium quantized tiny embedded_csv missing original raw sampled small".split(" ")
    for d in dirs:
        print("CREATING_DIRECTORY_IF_NEEDED" , "data/" + d)
        create_dir_if_needed("data/" + d)
    
def save_all():
    create_all_dirs_if_needed()
    save_all_classification_datasets()
    save_all_regression_datasets()

save_all()
