import pybaseball as pyb
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Batting Points
single = 1
double = 2
triple = 3
hr = 4
bb = 1
r = 1
rbi = 1
sb = 2
k = -1
cs = -1

# Pitching Points
ip = 3
sv = 5
h = -1
hd = 5
er = -2
so = 1
bbp = -1
qs = 5

# Some other information (make sure this is correct so the program can figure out which picks were yours)
numteams = 10
yourpick = 1

sourcenames = ['fans','steamer','zips','thebat','atc']
batpositions = ['c','1b','2b','ss','3b','of','dh']
sourcedata = []
combineddata = []
for position in batpositions:
    dc = pd.read_csv('data\\' + position + '_dc' + '.csv').set_index('Name')
    for source in sourcenames:
        sourcedata += [pd.read_csv('data\\' + position + '_' + source + '.csv').set_index('Name')]
    combined = pd.concat(sourcedata).groupby(level=0).sum()
    points = ((combined['H']*single + combined['2B']*double + combined['3B']*triple + combined['HR']*hr + combined['BB']*bb + combined['R']*r + combined['RBI']*rbi + combined['SB']*sb + combined['SO']*k + combined['CS']*cs)/combined['AB'])*dc['AB']
    combined['POINTS'] = points
    combined['% POINTS'] = (100*points/points.sum())
    combined['ADP'] = dc['ADP']
    combined = combined[pd.notnull(combined['POINTS'])]
    combined = combined[combined['POINTS'] != 0]
    combined['Position'] = position.upper()
    combined.sort_values('% POINTS',ascending=False).to_csv('data\\' + position + '_combined.csv')
    combineddata += [combined]

dc = pd.read_csv('data\\p_dc' + '.csv').set_index('Name')
for source in sourcenames:
    sourcedata += [pd.read_csv('data\\p_' + source + '.csv').set_index('Name')]
combined = pd.concat(sourcedata).groupby(level=0).mean()
points = ((combined['H']*h + combined['SV']*sv + combined['ER']*er + combined['BB']*bbp + combined['IP']*ip + combined['W']*qs + combined['SO']*so)/combined['IP'])*dc['IP']
combined['POINTS'] = points
combined['% POINTS'] = (100*points/points.sum())
combined['ADP'] = dc['ADP']
combined = combined[pd.notnull(combined['POINTS'])]
combined = combined[combined['POINTS'] != 0]
combined['Position'] = 'SP'
combined.loc[combined['SV'] > 0,'Position'] = 'RP'
combined.sort_values('% POINTS',ascending=False).to_csv('data\\p_combined.csv')
combineddata += [combined]

totalcombined = pd.concat(combineddata)
totalcombined = totalcombined.sort_values('% POINTS',ascending=True).drop_duplicates('POINTS').sort_index()
totalcombined = totalcombined.sort_values('ADP')
totalcombined['INDEX'] = range(1,len(totalcombined)+1)
totalcombined = totalcombined.reset_index()
totalcombined = totalcombined.set_index('INDEX')
totalcombined.to_csv('data\\total.csv')
draftpick = 1

while(1):
    showrange = 0
    top25 = totalcombined[['Name','Position','POINTS','% POINTS','ADP']].sort_values('ADP').set_index('Name')
    top25['INDEX'] = range(1,len(top25)+1)
    top25 = top25.reset_index()
    top25 = top25.set_index('INDEX')
    print('You should pick: ' + top25[0:numteams*2].sort_values('% POINTS',ascending=False).reset_index().loc[0]['Name'])
    print('Other options:')
    print(top25[showrange:showrange+25])
    print('')
    while(1):
        print('Commands: n (show next 25), l (lookup by name), d (see your drafted players), f (finish)')
        print('Enter a number from the list or a player name to draft that player.')
        print('')
        pick = input('Pick at ' + str(draftpick) + ': ')
        print('\n')
        if pick == 'n':
            showrange += 25
            print(top25[showrange:showrange+25])
            print('\n')
        else:
            break
    try:
        value = int(pick)
        value = top25.loc[value]['Name']
        pick = totalcombined.loc[totalcombined['Name'] == value][['Name','Position','POINTS','% POINTS','ADP']][0:1]
        pick['Drafted'] = draftpick
        if (draftpick == yourpick):
            yourdraft = pick
        elif (draftpick%(numteams*2) == yourpick) or (draftpick%(numteams*2) == ((numteams*2+1)-yourpick)%(numteams*2)):
            yourdraft = pd.concat([yourdraft, pick]) 
        totalcombined = totalcombined[totalcombined['Name'] != value]
        draftpick += 1
    except:
        value = pick
        if value in totalcombined['Name'].unique():
            pick = totalcombined.loc[totalcombined['Name'] == value][['Name','Position','POINTS','% POINTS','ADP']][0:1]
            pick['Drafted'] = draftpick
            if (draftpick == yourpick):
                yourdraft = pick
            elif (draftpick%(numteams*2) == yourpick) or (draftpick%(numteams*2) == ((numteams*2+1)-yourpick)%20):
                yourdraft = pd.concat([yourdraft,pick])
            totalcombined = totalcombined[totalcombined['Name'] != value]
            draftpick += 1
            print('Picked ' + value + '.\n')
        elif value == 'l':
            while(1):
                lookup = input('Enter name to lookup (q to return): ')
                if lookup in totalcombined['Name'].unique():
                    print(totalcombined.loc[totalcombined['Name'] == lookup][['Name','Position','POINTS','% POINTS','ADP']])
                elif lookup == 'q':
                    break
                else:
                    print('No match!')
        elif value == 'd':
            print(yourdraft.set_index('Drafted'))
            print('\n')
            input('Press ENTER to return')
        elif value == 'f':
            yourdraft.set_index('Drafted').to_csv('yourdraft.csv')
            print(yourdraft.set_index('Drafted'))
            print('\n')
            input('Press ENTER to quit.')
            exit(0)
        else:
            print('Invalid player name.\n')
