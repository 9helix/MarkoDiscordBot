import pickle

x = []
with open('database/times.pkl', 'wb') as f:
    pickle.dump(x, f)
