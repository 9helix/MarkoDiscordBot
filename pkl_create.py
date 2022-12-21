import pickle

x = {}
with open('database/follow_dict.pkl', 'wb') as f:
    pickle.dump(x, f)
