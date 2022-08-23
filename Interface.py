import streamlit as st
import pandas as pd
import pickle
import itertools


# Loading Model
with open("model.pickle", 'rb') as r:
    loaded_mod = pickle.load(r)

# Getting all datasets we need. Player Role Database and Player stats Database
roles = pd.read_csv(r"/Users/simonlee/Desktop/Capstone/Data/roles1.csv")
stats = pd.read_csv(r"/Users/simonlee/Desktop/Capstone/Data/Player Stats Generated.csv")


#Creating Stats Dictionary
stats_dict = {}
for x, y in stats.iterrows():
    stats_dict[y["ID"]] = y["Batting Index"]


# Making a Player Role Dictionary
player_dict  = {}
for x, y in roles.iterrows():
    player_dict[y["ID"]]= [y["Full Name"], y["Player Role Cleaned"], y["Batting Style"], y["Bowling Style Cats"]]

#Create Dictionary for Countries
country_dict = {}
index = 0
for c in ['Australia', 'England', 'NZ', 'SA', 'Sub-Cont', 'UK', 'WI', 'Zimb']:
    country_dict[c] = index
    index = index + 1


#Function to get the player information for a team
def get_player_info(list_ids):
    step_1 = []
    for id in list_ids:
        step_1.append(player_dict[id])
    return step_1


#Function to get Index of teams
def get_team_index (list_ids):
    total = 0
    for id in list_ids:
        total = total + stats_dict[id]
    
    return total

#Function to get composition of team 
def get_comps (list_ids):
    step_1 = get_player_info(list_ids)

    lhb = 0
    rhb = 0
    nb = 0

    laf = 0
    raf = 0
    las = 0
    ras = 0
    raws = 0
    laws = 0
    nbowl = 0

    tob = 0
    ba = 0
    a = 0
    bowla = 0
    w = 0
    batter = 0
    mob = 0
    ob = 0
    bowler = 0


    for o in step_1:
        #Batting Style
        if o[2] == "Left hand Bat":
            lhb = lhb + 1
        elif o[2] == "Right hand Bat":
            rhb = rhb + 1
        else:
            nb = nb +1
        
        #Bowling Styles
        if o[3] == "Left Arm Fast":
            laf = laf + 1
        elif o[3] == "Right Arm Fast":
            raf = raf + 1
        elif o[3] == "Right Arm Spinner":
            ras = ras + 1
        elif o[3] == "Left Arm Spinner":
            las = las + 1
        elif o[3] == "Right Arm Wrist Spinner":
            raws = raws + 1
        elif o[3] == "Left Arm Wrist Spinner":
            laws = laws + 1
        elif o[3] == "NoBowl":
            nbowl = nbowl + 1
        
        #Player Roles
        if o[1] == "Top order Batter":
            tob = tob + 1
        elif o[1] == "Bowling Allrounder":
            bowla = bowla + 1
        elif o[1] == "Wicketkeeper":
            w = w + 1
        elif o[1] == "Allrounder":
            a = a + 1
        elif o[1] == "Batting Allrounder":
            ba = ba + 1
        elif o[1] == "Batter":
            batter = batter + 1
        elif o[1] == "Middle order Batter":
            mob = mob + 1
        elif o[1] == "Opening Batter":
            ob = ob + 1
        elif o[1] == "Bowler":
            bowler = bowler + 1
        

    e_comp = [lhb, nb, rhb, laws, ras, laf, raf, nbowl, las, raws, tob, bowla, w, a, ba, batter, mob, ob, bowler]
    return(e_comp)


#Function to get all possible combinations of players in selection pool
def get_all_combinations(selection_pool):
    possible_teams = list(itertools.combinations(selection_pool, 11))
    possible_comps = {}
    possible_teams1 ={}
    for i in range (0, len(possible_teams)):
        #Ensuring team has at least 2 out and out bowlers and at least 3 specialist batsmen and 1 wicketkeeper
        if get_comps(list(possible_teams[i]))[18]>= 2 and (get_comps(list(possible_teams[i]))[10] + get_comps(list(possible_teams[i]))[16] + get_comps(list(possible_teams[i]))[17])>=4 and get_comps(list(possible_teams[i]))[12]>=1 and (get_comps(list(possible_teams[i]))[18] + get_comps(list(possible_teams[i]))[14] + get_comps(list(possible_teams[i]))[13] + get_comps(list(possible_teams[i]))[11])>=5:
            possible_comps[i] = get_comps(list(possible_teams[i]))
            possible_teams1[i] = list(possible_teams[i])
    return possible_comps, possible_teams1


#Function to Recommend A team
def recommend (selection_pool, expected_11, country):
    possible_comps = get_all_combinations(selection_pool)[0]
    possible_teams1 = get_all_combinations(selection_pool)[1]
    highest = 0
    for i in possible_comps.keys():
        z = []
        for b in range(0, len(possible_comps[i])):
            z.append(possible_comps[i][b])
            z.append(get_comps(expected_11)[b])
        if loaded_mod.predict_proba([z + [country]])[0][0] > highest:
            best = possible_comps[i]
            highest = loaded_mod.predict_proba([possible_comps[i] + get_comps(expected_11) + [country]])[0][0]

    narrowed_down = {}
    for key in possible_comps.keys():
        if possible_comps[key] == best:
            narrowed_down[key] = possible_teams1[key]

    high = 0
    for key in list(narrowed_down.keys()):
        if get_team_index(narrowed_down[key]) > high:
            best_team = narrowed_down[key]
            high = get_team_index(narrowed_down[key])

    st.write("""
    # RESULTS

    ### Recommended Team Composition
    """)

    st.write("Recommended Team Composition that gives a", round(highest*100, 2), "% chance of victory is as follows...")
    st.write("Number of Left Hand Batters:", best[0])
    st.write("Number of Right Hand Batters:", best[2])
    st.write("Number of No Bat:", best[1])
    st.write("Number of Left Arm Wrist Spinners:", best[3])
    st.write("Number of Right Arm Wrist Spinners:", best[9])
    st.write("Number of Left Arm Fast Bowlers:", best[5])
    st.write("Number of Right Arm Fast Bowlers:", best[6])
    st.write("Number of Left Arm Spinners:", best[8])
    st.write("Number of Right Arm Spinners:", best[4])
    st.write("Number of No Bowl:", best[7])
    st.write("Number of Top Order Batters:", best[10])
    st.write("Number of Opening Batters:", best[17])
    st.write("Number of Middle Order Batters:", best[16])
    st.write("Number of Batting Allrounders:", best[14])
    st.write("Number of Allrounders:", best[13])
    st.write("Number of Bowling Allrounders:", best[11])
    st.write("Number of Bowlers:", best[18])
    st.write("Number of Wicketkeepers:", best[12])

    st.write("""
    ## Selection Process

    """)
    st.write("There were", len(narrowed_down), "possible teams that could have been selected with this composition!")
    st.write("The team that was chosen, with the highest team batting index of", round(high, 2), "is...")
    
    #Writing to dataframe
    selected = []
    selected.append(get_player_info(best_team)[0])
    selected.append(get_player_info(best_team)[1])
    selected.append(get_player_info(best_team)[2])
    selected.append(get_player_info(best_team)[3])
    selected.append(get_player_info(best_team)[4])
    selected.append(get_player_info(best_team)[5])
    selected.append(get_player_info(best_team)[6])
    selected.append(get_player_info(best_team)[7])
    selected.append(get_player_info(best_team)[8])
    selected.append(get_player_info(best_team)[9])
    selected.append(get_player_info(best_team)[10])

    selected_df = pd.DataFrame(data = selected, columns = ["Full Name", "Player Role", "Batting Style", "Bowling Style" ])
    st.table(selected_df)
    


st.write("""

# WELCOME TO SIMON'S T20 CRICKET TEAM SELECTOR


""")




#SELECTION POOL ENTRY
st.write ("""
## Step 1: Selection Pool

* Please enter the IDs of the players in your selection pool.
""")


id_p1 = st.text_input('Selection Squad Player 1 ID', 'Please enter a valid ID here...')

if id_p1 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p1][0], "has been selected")


id_p2 = st.text_input('Selection Squad Player 2 ID', 'Please enter a valid ID here...')

if id_p2 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p2][0], "has been selected")


id_p3 = st.text_input('Selection Squad Player 3 ID', 'Please enter a valid ID here...')

if id_p3 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p3][0], "has been selected")



id_p4 = st.text_input('Selection Squad Player 4 ID', 'Please enter a valid ID here...')

if id_p4 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p4][0], "has been selected")


id_p5 = st.text_input('Selection Squad Player 5 ID', 'Please enter a valid ID here...')

if id_p5 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p5][0], "has been selected")




id_p6 = st.text_input('Selection Squad Player 6 ID', 'Please enter a valid ID here...')

if id_p6 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p6][0], "has been selected")


id_p7 = st.text_input('Selection Squad Player 7 ID', 'Please enter a valid ID here...')

if id_p7 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p7][0], "has been selected")




id_p8 = st.text_input('Selection Squad Player 8 ID', 'Please enter a valid ID here...')

if id_p8 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p8][0], "has been selected")



id_p9 = st.text_input('Selection Squad Player 9 ID', 'Please enter a valid ID here...')

if id_p9 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p9][0], "has been selected")




id_p10 = st.text_input('Selection Squad Player 10 ID', 'Please enter a valid ID here...')

if id_p10 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p10][0], "has been selected")


id_p11 = st.text_input('Selection Squad Player 11 ID', 'Please enter a valid ID here...')

if id_p11 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p11][0], "has been selected")



id_p12 = st.text_input('Selection Squad Player 12 ID', 'Please enter a valid ID here...')

if id_p12 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p12][0], "has been selected")



id_p13 = st.text_input('Selection Squad Player 13 ID', 'Please enter a valid ID here...')

if id_p13 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p13][0], "has been selected")



id_p14 = st.text_input('Selection Squad Player 14 ID', 'Please enter a valid ID here...')

if id_p14 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p14][0], "has been selected")



id_p15 = st.text_input('Selection Squad Player 15 ID', 'Please enter a valid ID here...')

if id_p15 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p15][0], "has been selected")


id_p16 = st.text_input('Selection Squad Player 16 ID', 'Please enter a valid ID here...')

if id_p16 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id_p16][0], "has been selected")


selection_pool = [id_p1, id_p2, id_p3, id_p4, id_p5, id_p6, id_p7, id_p8, id_p9, id_p10, id_p11, id_p12, id_p13, id_p14, id_p15, id_p16]



try:
    st.write("This is the squad you have available...")
    st.write("1.", player_dict[id_p1][0], "------", player_dict[id_p1][1])
    st.write("2.", player_dict[id_p2][0], "------", player_dict[id_p2][1])
    st.write("3.",player_dict[id_p3][0], "------", player_dict[id_p3][1])
    st.write("4.",player_dict[id_p4][0], "------", player_dict[id_p4][1])
    st.write("5.",player_dict[id_p5][0], "------", player_dict[id_p5][1])
    st.write("6.",player_dict[id_p6][0], "------", player_dict[id_p6][1])
    st.write("7.",player_dict[id_p7][0], "------", player_dict[id_p7][1])
    st.write("8.",player_dict[id_p8][0], "------", player_dict[id_p8][1])
    st.write("9.",player_dict[id_p9][0], "------", player_dict[id_p9][1])
    st.write("10.",player_dict[id_p10][0], "------", player_dict[id_p10][1])
    st.write("11.",player_dict[id_p11][0], "------", player_dict[id_p11][1])
    st.write("12.",player_dict[id_p12][0], "------", player_dict[id_p12][1])
    st.write("13.",player_dict[id_p13][0], "------", player_dict[id_p13][1])
    st.write("14.",player_dict[id_p14][0], "------", player_dict[id_p14][1])
    st.write("15.",player_dict[id_p15][0], "------", player_dict[id_p15][1])
    st.write("16.",player_dict[id_p16][0], "------", player_dict[id_p16][1])
except:
    print("Players of Opposition not entered as yet")
    





#EXPECTED OPPOSITION ENTRY
st.write ("""
## Step 2: Expected Opposition Team Selection

* Please enter the IDs of the players expected to be in the opposition's team
""")

id1 = st.text_input('Opposition Player 1 ID', 'Please enter a valid ID here...')

if id1 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id1][0], "has been selected")


id2 = st.text_input('Opposition Player 2 ID', 'Please enter a valid ID here...')

if id2 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id2][0], "has been selected")


id3 = st.text_input('Opposition Player 3 ID', 'Please enter a valid ID here...')

if id3 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id3][0], "has been selected")



id4 = st.text_input('Opposition Player 4 ID', 'Please enter a valid ID here...')

if id4 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id4][0], "has been selected")


id5 = st.text_input('Opposition Player 5 ID', 'Please enter a valid ID here...')

if id5 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id5][0], "has been selected")




id6 = st.text_input('Opposition Player 6 ID', 'Please enter a valid ID here...')

if id6 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id6][0], "has been selected")


id7 = st.text_input('Opposition Player 7 ID', 'Please enter a valid ID here...')

if id7 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id7][0], "has been selected")




id8 = st.text_input('Opposition Player 8 ID', 'Please enter a valid ID here...')

if id8 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id8][0], "has been selected")



id9 = st.text_input('Opposition Player 9 ID', 'Please enter a valid ID here...')

if id9 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id9][0], "has been selected")




id10 = st.text_input('Opposition Player 10 ID', 'Please enter a valid ID here...')

if id10 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id10][0], "has been selected")


id11 = st.text_input('Opposition Player 11 ID', 'Please enter a valid ID here...')

if id11 not in list(player_dict.keys()):
    st.write('Player Id is Invalid ')
else:
    st.write(player_dict[id11][0], "has been selected")


expected_11 = [id1, id2, id3, id4, id5, id6, id7, id8, id9, id10, id11]


try:
    st.write("This is the team you are expected to play against...")
    st.write("1.", player_dict[id1][0], "------", player_dict[id1][1])
    st.write("2.", player_dict[id2][0], "------", player_dict[id2][1])
    st.write("3.",player_dict[id3][0], "------", player_dict[id3][1])
    st.write("4.",player_dict[id4][0], "------", player_dict[id4][1])
    st.write("5.",player_dict[id5][0], "------", player_dict[id5][1])
    st.write("6.",player_dict[id6][0], "------", player_dict[id6][1])
    st.write("7.",player_dict[id7][0], "------", player_dict[id7][1])
    st.write("8.",player_dict[id8][0], "------", player_dict[id8][1])
    st.write("9.",player_dict[id9][0], "------", player_dict[id9][1])
    st.write("10.",player_dict[id10][0], "------", player_dict[id10][1])
    st.write("11.",player_dict[id11][0], "------", player_dict[id11][1])
except:
    print("No Player Selected as yet")




# SELECT COUNTRY/REGION

st.write ("""
## Step 3: Selection of Country/Region Match is being played

* Select where this match is to be played
""")


country = st.selectbox("Country/Region", ['Australia', 'England', 'NZ', 'SA', 'Sub-Cont', 'UK', 'WI', 'Zimbabwe'])

c_index =  country_dict[country]


try:
    recommend(selection_pool, expected_11, c_index)
except:
    print("No info available, ensure all is filled out")