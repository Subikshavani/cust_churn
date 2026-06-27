from .modeling import train_and_select_best_model

if __name__ == "__main__":
    result = train_and_select_best_model()
    print(result.best_model_name)
