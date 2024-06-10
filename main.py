import random 
import pandas as pd
import os
import shutil

#Defining the genes
class Course:
    def __init__(self, course_id, name, duration, type_, program):
        self.course_id = course_id
        self.name = name
        self.duration = duration
        self.type = type_
        self.program = program
    def __repr__(self):
        return self.course_id
    def __str__(self):
        return self.course_id

class Professor:
    def __init__(self, prof_id, name):
        self.prof_id = prof_id
        self.name = name
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    
class Room:
    def __init__(self, room_type,id_):
        self.room_type = room_type
        self.id=id_

    def __repr__(self):
        return self.id
    def __str__(self):
        return self.id

class Gap:
    def __init__(self, duration):
        self.duration=duration

    def __repr__(self):
        return str(self.duration)
    def __str__(self):
        return str(self.duration)

# Define the gene set for courses
courses_gene_set = {
    'CS101': Course('CS101', 'Introduction to Computer Science', 2, 'Lecture', 'CS'),
    'CS202': Course('CS202', 'Data Structures', 2, 'Lecture', 'CS'),
    'CS303': Course('CS303', 'Algorithms', 3, 'Lecture', 'CS'),
    'CS404': Course('CS404', 'Software Engineering', 3, 'Lecture', 'CS'),
    'CS505': Course('CS505', 'Artificial Intelligence', 3, 'Lecture', 'CS'),

    'IS201': Course('IS201', 'Database Management', 3, 'Lecture', 'IS'),
    'IS301': Course('IS301', 'Data Mining', 3, 'Lecture', 'IS'),
    'IS403': Course('IS403', 'Business Intelligence', 3, 'Lecture', 'IS'),
    'IS504': Course('IS504', 'Big Data Analytics', 3, 'Lecture', 'IS'),
    'IS605': Course('IS605', 'Information Systems Security', 3, 'Lecture', 'IT'),

    'IT101': Course('IT101', 'Programming Fundamentals', 2, 'Lecture', 'IT'),
    'IT301': Course('IT301', 'Network Security', 2, 'Lecture', 'IT'),
    'IT403': Course('IT403', 'Cybersecurity Fundamentals', 3, 'Lecture', 'IT'),
    'IT504': Course('IT504', 'Cloud Computing', 3, 'Lecture', 'IT'),
    'IT605': Course('IT605', 'Web Development', 3, 'Lecture', 'IS'),
}

# Define the gene set for professors
professors_gene_set = {
    'P1': Professor('P1', 'Prof. Smith'),
    'P2': Professor('P2', 'Prof. Johnson'),
    'P3': Professor('P3', 'Prof. Brown'),
    'P4': Professor('P4', 'Prof. Lee'),
    'P5': Professor('P5', 'Prof. White'),
    'P6': Professor('P6', 'Prof. Green'),
}

# Define the gene set for rooms
rooms_gene_set = {
    'Hall1': Room('Hall','Hall1'),
    'Hall2': Room('Hall','Hall2'),
    'Hall3': Room('Hall','Hall3'),
    'Lab1': Room('Lab','Lab1'),
    'Lab2': Room('Lab','Lab2'),
    'Lab3': Room('Lab','Lab3'),
    'Lab4': Room('Lab','Lab4'),
    'Lab5': Room('Lab','Lab5'),
}

#Define gaps geneset
gaps_gene_set = {
    "gap_1h":Gap(1)
    ,"gap_2h":Gap(2)
    ,"gap_3h":Gap(3)
}


#defining the pool generator
def create_pool():
    programs=['CS','IT','IS']
    time_slots = [8,8,8]  # Specify the number of time slots for every program per individual
    pool=[[],[],[]]  
    for i in range(3):
        courses=[c for c in courses_gene_set.keys() if courses_gene_set[c].program == programs[i]] # you need to go back to modify this so that it can return the remaining courses for other days
        if len(courses)==0:
            pool[i].append(Gap(8))
        while time_slots[i] > 0 and len(courses) > 0:
            if random.choice([0, 1]) == 1:  # Randomly decide whether to insert a gap, (modify it so that the choice is based on the GAP_PROB)
                gap = random.choice(list(gaps_gene_set.values()))  #can it be just 1 hour gap?
                if gap.duration <= time_slots[i]:
                    pool[i].append(gap)
                    time_slots[i] -= gap.duration
            else:  # Insert a gene (course, professor, room)
                course_id = random.choice(courses)
                prof_id = random.choice(list(professors_gene_set.keys()))
                room_id = random.choice(list(rooms_gene_set.keys()))
                course_duration = courses_gene_set[course_id].duration
                if course_duration <= time_slots[i]:
                    gene = (courses_gene_set[course_id], professors_gene_set[prof_id], rooms_gene_set[room_id])
                    pool[i].append(gene)
                    time_slots[i] -= course_duration
    return pool

#turn the pool into a schedule
def pool_to_schedule(pool):
    schedule = {i:[] for i in range(8)}        
    pointers=[0,0,0]
    for i in range(3):
        for j in pool[i]:
            if type(j)==Gap:
                for k in range(j.duration):
                    schedule[pointers[i]].append(j)
                    pointers[i]+=1
            else:
                for k in range(j[0].duration):
                    schedule[pointers[i]].append(j)
                    pointers[i]+=1
    return schedule

# Initialize population function
def initialize_population(pop_size):
    population = []
    pools=[]
    for _ in range(pop_size):
        pool=create_pool()
        pools.append(pool)
        schedule = pool_to_schedule(pool)
        population.append(schedule)
    return [pools,population]

def calc_gap_fitness(pool): #calculates fitness based on how the gaps are distributed so that in an ideal pool there shoudln't be an empty day, the lectures are close to eachother and there shoudln't be many gaps for no reason
    res=0
    for i in range(3):
        m=len(pool[i])
        head=pool[i][:m//2]
        tail=pool[i][-m//2:]
        tail.reverse()
        c=False
        for j in head:
            if type(j)!=Gap:
                c=True
            else:
                if c:
                    res-=j.duration
                else:
                    res-=1
        c=False
        for j in tail:
            if type(j)!=Gap:
                c=True
            else:
                if c:
                    res-=j.duration
                else:
                    res-=1
    return res


def fitness(pool,schedule): #calculates fitness based on an ideal schedule where there shoudln't be conflicting courses or proffessors at the same time, an ideal pool where there shouldn't two or of the same course or lab at the same time and a program's pool length is between 4 and 6 hours and the fitness is also based the pre calculated gap fitness
    pool_len=[sum(pool[i][j][0].duration for j in range(len(pool[i])) if type(pool[i][j])!=Gap) for i in range(3)]
    gap_fitness=0
    conflicts=0
    for program in pool:
        for i in range(len(program)):
            if type(program[i])!=Gap:
                for j in range(i+1,len(program)):
                    if type(program[j])!=Gap:
                        if program[i][0]==program[j][0] and program[i][2].room_type==program[j][2].room_type:
                            conflicts-=1

    for i in range(8):
        if schedule[i]!=[]: #slot
            for k in range(len(schedule[i])):
                if type(schedule[i][k])!=Gap: # lecture or lab
                    for l in range(k+1,len(schedule[i])):
                            if type(schedule[i][l])!=Gap:
                                if schedule[i][k][0]==schedule[i][l][0]: #course conflict
                                    conflicts-=1
                                if schedule[i][k][1]==schedule[i][l][1]: #prof conflict
                                    conflicts-=1
    gap_fitness=calc_gap_fitness(pool) # gap fitness
    tiring=sum(-1 for i in pool_len if i>6 or i < 4)
    return conflicts+gap_fitness+tiring
    
def cross_over(pool1, pool2):# single point crossover
    p=random.randint(0,2)
    ch1=pool1.copy()
    ch2=pool2.copy()
    ch1[p],ch2[p]=ch2[p],ch1[p]
    return ch1,ch2

def new_generation(population,fitnesses): # generates a new population from the two best fitness parents and the worst two
    prnt1,prnt2=fitnesses[:2]
    ch1,ch2=cross_over(population[0][prnt1],population[0][prnt2])
    sch1,sch2=pool_to_schedule(ch1),pool_to_schedule(ch2)
    p1,p2=fitnesses[-2:]
    population[0][p1],population[0][p2]=ch1,ch2
    population[1][p1],population[1][p2]=sch1,sch2
    return population

def mutate(pool,rate): #mutates the pool in a certain rate
    if random.random() < rate:
        for i in range(3):
            random.shuffle(pool[i])

def modify_courses(pool): #removes used courses from the course gene set
    for p in range(3):
        for course in pool[p]:
            if type(course)!=Gap:
                id_=course[0].course_id
                courses_gene_set.pop(id_,None)

def evolution(MAX_GENERATION=200,POPULATION_SIZE=100,MUTATION_RATE=0.5):
    print("--new--")
    population=initialize_population(POPULATION_SIZE) # initialize population
    pools,schedules=population
    # calculate fitness
    fitnesses={i:fitness(pools[i],schedules[i]) for i in range(POPULATION_SIZE)}
    fitnesses_i=sorted(fitnesses,key=lambda x: fitnesses[x],reverse=True)
    # get the best fitness for comarison
    best_child=population[1][fitnesses_i[0]]
    best_fitness=fitnesses[fitnesses_i[0]]
    for gen in range(MAX_GENERATION):
        pools,schedules=new_generation(population,fitnesses_i)
        for i in range(POPULATION_SIZE):
            mutate(pools[i],MUTATION_RATE)
        for i in range(POPULATION_SIZE):
            schedules[i]=pool_to_schedule(pools[i])
        population=[pools,schedules]
        fitnesses={i:fitness(pools[i],schedules[i]) for i in range(POPULATION_SIZE)}
        fitnesses_i=sorted(fitnesses,key=lambda x: fitnesses[x],reverse=True)
        if fitnesses[fitnesses_i[0]]>best_fitness:
            best_child=population[1][fitnesses_i[0]]
            best_fitness=fitnesses[fitnesses_i[0]]
            # print('Gen:',gen,'Best:',schedules[fitnesses_i[0]],'Fitness:',best_fitness)
            print('Gen:',gen,'Fitness:',best_fitness)
        if best_fitness==0:
            # print('Solved in Gen:',gen,'Best:',schedules[fitnesses_i[0]],'Fitness:',best_fitness)
            print('Solved in Gen:',gen,'Fitness:',best_fitness)
            break
    modify_courses(pools[fitnesses_i[0]])
    print(f'best fitness: {best_fitness}')
    return [pools[fitnesses_i[0]],schedules[fitnesses_i[0]]]
        
def create_day(schedule): # turns a schedule into a pandas dataframe
    sch=schedule.copy()
    for i in range(8):
        for j in range(len(sch[i])):
            if type(sch[i][j])==Gap:
                sch[i][j]='--'
    df = pd.DataFrame(index=['CS', 'IT', 'IS'], columns=sch.keys())
    for key, values in sch.items():
        df[key] = values
    return df

def main(): # creats days untill there are no more courses
    cwd=os.getcwd()
    dirc="days"
    path=os.path.join(cwd,dirc)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    #
    raw=[]
    days={}
    while len(courses_gene_set)>0:
        raw.append(evolution()[1])
    for day in range(len(raw)):
        for key in range(len(raw[day])):
            for slot in range(len(raw[day][key])):
                if type(raw[day][key][slot]) != Gap:
                    raw[day][key][slot]=list(raw[day][key][slot])
                    for course in range(len(raw[day][key][slot])):
                        raw[day][key][slot][course]=str(raw[day][key][slot][course])
        days[day]=create_day(raw[day])

    week = pd.concat(days.values(), ignore_index=True)
    print(f"week shape: {week.shape[0]}")
    #
    for i in range(len(days)):
        days[i].to_csv(os.path.join(path,f'day {i+1}.csv'))
    week.to_csv(os.path.join(path,'week.csv'))
    print(len(courses_gene_set),len(days))
    #
    # GUI
    import tkinter as tk
    from tkinter import ttk
    #window
    window=tk.Tk()
    window.geometry('720x750')
    window.title('Schedule')
    #treeview
    table=ttk.Treeview(window,columns=list(week.columns),show='headings')
    table.pack(fill='both',expand=True)
    #adjust row height and style
    style = ttk.Style()
    style.configure("Treeview", rowheight=40, font=("Helvetica", 8))
#
    table.tag_configure('oddrow', background='#E8E8E8')
    table.tag_configure('evenrow', background='#DFDFDF')
    table.tag_configure('dayrow', background='#A2AAB3')
#
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    #adjust column width
    for i in week.columns:
        table.heading(f"{i}", text=f"{i+8}:00")
        table.column(f"{i}", minwidth=50, width=90, stretch=False)
    #inserting data
    days_names={0:'sunday',3:'monday',6:'tuesday',9:'wednesday',12:'thursday'}
    for i in range(week.shape[0]):
        row=[]
        for cell in week.iloc[i]:
            if type(cell)==str:
                row.append(cell)
            else:
                cell='\n'.join(cell)
                row.append(cell)
        if i%3==0:
            d=[days_names[i]]*8
            table.insert('',tk.END,values=d,tags=('dayrow'))
        table.insert('',tk.END,values=row,tags=('evenrow' if i % 2 == 0 else 'oddrow'))
    window.mainloop()
# main()
chromosome=evolution()
pool=chromosome[0]
schedule=chromosome[1]
print(chromosome)
print('-------------------------')
print(pool)
print('-------------------------')
print(schedule)
