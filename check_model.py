import pickle

# 1) Point to your model file
MODEL_PATH = "app/models/proj_model_1628978_202425.pkl"

# 2) Load it
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# 3) Try predicting cumulative points at, say, game 50
game_num = [[50]]     # note: sklearn expects a 2D array
cumulative_at_50 = model.predict(game_num)[0]
print(f"Predicted cumulative points through 50 games: {cumulative_at_50:.1f}")

# 4) Project full season (82 games)
full_season = [[82]]
projected_total = model.predict(full_season)[0]
print(f"Projected season total: {projected_total:.1f} points")
print(f"Which is {projected_total/82:.2f} PPG on average")
