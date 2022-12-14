import pickle

x = {}
y = []
with open('database/follow_dict.pkl', 'wb') as f:
    pickle.dump([x, y], f)
