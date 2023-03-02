import tensorflow as tf
import numpy as np
import pprint

from src.core.logger import logger
from src.ai.state_save import StateSaveDecoder
from sklearn.model_selection import train_test_split


def load_data():
    decoder = StateSaveDecoder()
    return decoder.data

# convert np.uint64 to array of 64 bits
def bits_to_array(bits: np.uint64) -> np.ndarray:
    return np.array([int(b) for b in bin(bits)[2:].zfill(64)], dtype=np.uint64)


def sanitize_data():
    data = load_data()
    bits_black = np.array([bits_to_array(np.uint64(data[i]['bits_black'])) for i in range(len(data))])
    bits_white = np.array([bits_to_array(np.uint64(data[i]['bits_white'])) for i in range(len(data))])
    current_player = np.array([data[i]['current_player'] for i in range(len(data))], dtype=np.int8)
    results = [data[i]['results'] for i in range(len(data))]

    x_train = np.column_stack((bits_black, bits_white, current_player))
    y_train = np.zeros((len(results), 64))

    for i in range(len(results)):
        for r in results[i]:
            move = int(list(r.keys())[0])
            ratio = float(r[str(move)]['ratio'])
            y_train[i][move] = ratio

    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train,
                                                        test_size=0.2, random_state=42)

    return x_train, x_test, y_train, y_test

def train():
    x_train, x_test, y_train, y_test = sanitize_data()

    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(129,)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=8000)

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)

    logger.info(f'Test accuracy: {test_acc}, Test loss: {test_loss}')

    model.save('model.h5')

def load_and_test():
    np.set_printoptions(suppress=True)
    model = tf.keras.models.load_model('model.h5')

    x_train, x_test, y_train, y_test = sanitize_data()

    predictions = model.predict(x_test)

    for i in range(len(predictions)):
        pred = predictions[i]
        for j in range(len(pred)):
            if pred[j] < 0.01:
                pred[j] = 0

        print(f'Prediction:\n{pred}')
        print(f'Actual:\n{y_test[i]}')
        print(f'Error: {np.sum(np.abs(predictions[i] - y_test[i]))}')
        print()

