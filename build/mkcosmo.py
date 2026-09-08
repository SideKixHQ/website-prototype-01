# -*- coding: utf-8 -*-
"""James's quiz ideas, as five question quizzes.

His lists were shaped as a single question with the answers already written.
Flipping them makes each one a quiz: his options become the RESULTS, and five
questions underneath decide which you get. "What is your coffee order" stops
being the question and becomes the answer.

Every quiz is built on a grid so the shape checks pass by construction: the
same option count on every question, no two options in one question leading to
the same result, and each result leading a similar number of answers.
"""
import io, json, collections

OUT = "build/quizzes/%s.json"


def build(slug, title, kicker, intro, share, og, accent, results, questions,
          cta=None):
    keys = [r[0] for r in results]
    n = len(keys)
    qs = []
    for j, (text, opts) in enumerate(questions):
        assert len(opts) == len(questions[0][1]), "%s q%d option count" % (slug, j + 1)
        prim = [o[1] for o in opts]
        assert len(set(prim)) == len(prim), "%s q%d repeats a result" % (slug, j + 1)
        row = []
        for i, (a, primary) in enumerate(opts):
            sec = keys[(keys.index(primary) + 1 + ((i + j) % (n - 1))) % n]
            w = collections.OrderedDict([(primary, 3)])
            if sec != primary:
                w[sec] = 1
            row.append(collections.OrderedDict([("a", a), ("w", w)]))
        qs.append(collections.OrderedDict([("q", text), ("options", row)]))

    res = [collections.OrderedDict([
        ("key", k), ("name", nm), ("accent", ac), ("headline", hl),
        ("body", bd), ("cost", cost), ("art", ""),
    ]) for k, nm, ac, hl, bd, cost in results]

    q = collections.OrderedDict([
        ("slug", slug), ("title", title), ("kicker", kicker), ("intro", intro),
        ("share_line", share), ("accent", accent), ("og_line", og),
        ("cta", cta or collections.OrderedDict([
            ("title", "Something a bit more serious"),
            ("href", "../../assessment.html"),
            ("label", "The Energy Discovery"),
            ("blurb", "That one was for fun. The Energy Discovery is 48 statements "
                      "and returns how you actually work across all twelve energies."),
        ])),
        ("questions", qs), ("results", res),
    ])
    io.open(OUT % slug, "w", encoding="utf-8").write(
        json.dumps(q, indent=1, ensure_ascii=False))
    return slug


def main():
    made = []

    # ---- 1. coffee order -----------------------------------------------
    made.append(build(
        "coffee-order", "What is your founder coffee order?",
        "5 questions, about 30 seconds",
        "Nobody has ever been talked out of their order. This works out which "
        "one you are before you say it.",
        "My order is", "Five questions and the drink that gives you away.",
        "#B07A46",
        [("black","Black Coffee","#8A5A32","Let us get it done.",
          "No decoration, no ceremony, no discussion about the notes. You want the effect and you want it now.",
          "You mistake speed for progress about twice a quarter."),
         ("latte","Latte","#C9A06A","The strategic thinker.",
          "You want the good version and you will wait the extra four minutes for it. Everything you make gets one more pass than it strictly needs.",
          "The extra pass sometimes happens instead of shipping."),
         ("espresso","Espresso Shot","#E0483C","The chaos agent.",
          "All of it, immediately, standing up. You are the reason the group chat has 40 unread messages at 11pm.",
          "Everyone else needs a recovery day after your good ideas."),
         ("tea","Tea","#5FA98C","The calm operator.",
          "You have never once been the loudest person in a meeting and you have also never missed a deadline.",
          "People forget to ask your opinion because you never demand they do."),
         ("energy","Energy Drink","#7B5CC4","Founder after midnight.",
          "It is 1am, the thing is nearly working, and stopping now would be insane. You have had this conversation with yourself before.",
          "Tomorrow. Tomorrow is what it costs.")],
        [("It is 6am. Why are you awake?", [
            ("I always am. It is the quiet hour",              "black"),
            ("I am not. I am still up from yesterday",         "energy"),
            ("Slowly, with something warm, no screens yet",    "tea"),
            ("I woke up mid idea and had to write it down",    "espresso"),
            ("Alarm, gym, then the good coffee",               "latte")]),
         ("Someone books a meeting with no agenda.", [
            ("I ask what it is about before accepting",        "black"),
            ("I accept and prepare one for them",              "latte"),
            ("I accept. Something interesting usually happens","espresso"),
            ("I move it to the end of the week",               "tea"),
            ("I accept it and four others, same day",          "energy")]),
         ("Your to do list right now is:", [
            ("Three things, all of them real",                 "black"),
            ("Colour coded, and I enjoy that",                 "latte"),
            ("Six lists across four apps",                     "espresso"),
            ("One list, same one for years",                   "tea"),
            ("The list is a metaphor at this point",           "energy")]),
         ("A launch goes badly.", [
            ("Cut it, say so, move",                           "black"),
            ("Post mortem, then version two",                  "latte"),
            ("I already started the next thing during it",     "espresso"),
            ("Wait a week. It looks different by then",        "tea"),
            ("Fix it live, overnight, personally",             "energy")]),
         ("How does the work day end?", [
            ("When the thing is done",                         "black"),
            ("At a time I decided in advance",                 "latte"),
            ("Abruptly, mid sentence",                         "espresso"),
            ("Gently, and I do not check afterwards",          "tea"),
            ("It does not so much end as pause",               "energy")])]))

    # ---- 2. business energy today ---------------------------------------
    made.append(build(
        "energy-today", "Which business energy are you bringing today?",
        "5 questions, about 30 seconds",
        "Not who you are. Who you are being this week, which is a different "
        "question and usually a more useful one.",
        "Today I am bringing", "Five questions and the version of you that turned up this week.",
        "#D4A856",
        [("ceo","CEO Energy","#D4A856","Deciding things and meaning it.",
          "You are making calls today rather than gathering more input. The calendar bends around you instead of the other way round.",
          "Nobody tells you when you are wrong on a week like this."),
         ("mastermind","Mastermind Energy","#6FA8C4","Three moves ahead of the room.",
          "You are not doing the work today, you are working out which work is worth doing. Everyone else finds out on Thursday.",
          "A plan nobody has heard yet is not a plan, it is a secret."),
         ("hustle","Hustle Mode","#E0483C","Volume, speed, and no meetings.",
          "You are shipping. Not deciding, not planning, shipping. The inbox can wait and it knows it.",
          "You will be very tired on Friday and unsure exactly what moved."),
         ("survive","Just Trying to Survive","#8A8272","Still here, which counts.",
          "This is a week for keeping the lights on and the promises made. There is no shame in it and everybody has them.",
          "Nothing, if it is one week. Something, if it is the fourth in a row.")],
        [("The first thing you did this morning:", [
            ("Made a decision someone was waiting on",      "ceo"),
            ("Sat with the bigger question for a bit",      "mastermind"),
            ("Opened the thing and started building",       "hustle"),
            ("Worked out what could not slip today",        "survive")]),
         ("Your calendar this week:", [
            ("Cleared for the things that matter",          "ceo"),
            ("Two long blocks and nothing else",            "mastermind"),
            ("Packed, and I keep adding",                   "hustle"),
            ("Whatever survived the reshuffle",             "survive")]),
         ("Someone asks how it is going.", [
            ("Good. Here is what we decided",               "ceo"),
            ("Ask me in a month",                           "mastermind"),
            ("Busy. Really busy",                           "hustle"),
            ("Fine, and I change the subject",              "survive")]),
         ("An unexpected opportunity lands.", [
            ("Yes or no, today",                            "ceo"),
            ("Where does it sit in two years",              "mastermind"),
            ("Yes, obviously, I will find the time",        "hustle"),
            ("Not this week. Maybe next",                   "survive")]),
         ("What would actually help right now?", [
            ("Fewer people needing my answer",              "ceo"),
            ("An afternoon with no interruptions",          "mastermind"),
            ("Two more of me",                              "hustle"),
            ("One thing off the list",                      "survive")])]))

    # ---- 3. startup as a movie -------------------------------------------
    made.append(build(
        "startup-movie", "If your startup was a movie...",
        "5 questions, about 30 seconds",
        "Every business has a genre. Yours is showing whether you meant it to "
        "or not.",
        "My startup is", "Five questions and the film your business is quietly remaking.",
        "#C4534A",
        [("rocky","Rocky","#C4534A","Nobody picked you, and you went the distance.",
          "You were not the obvious choice and you are still standing, which is the entire point. The training montage is just your Tuesday.",
          "You have started to enjoy being the underdog more than winning would feel."),
         ("wolf","The Wolf of Wall Street","#D9A441","Loud, fast, and it is working.",
          "The energy is enormous and the numbers keep going up. Everyone in the room is slightly out of breath.",
          "Nobody in the room is asking the boring question about whether this holds."),
         ("social","The Social Network","#5B84B1","Built brilliantly, at a cost.",
          "The product is genuinely good and you know it. The complicated part was never the code.",
          "Look at who is still in the founding group photo."),
         ("mission","Mission Impossible","#7B5CC4","Impossible deadline, somehow met.",
          "You do your best work when the timer is already running. Every launch has one moment nobody outside the team knows about.",
          "You have started creating the emergencies yourself."),
         ("home","Home Alone","#5FA98C","Small, alone, and improvising brilliantly.",
          "It is you, some tools and a lot of ingenuity. The traps you build out of nothing are genuinely impressive.",
          "You have made being alone part of the identity, which makes help hard to accept.")],
        [("The best thing about your business right now:", [
            ("It should not work and it does",              "rocky"),
            ("The number went up again",                    "wolf"),
            ("The thing itself is really good",             "social"),
            ("We pulled off something last month",          "mission"),
            ("It is entirely mine",                         "home")]),
         ("Your last big win came from:", [
            ("Refusing to stop",                            "rocky"),
            ("Selling harder than anyone expected",         "wolf"),
            ("Building something nobody else had",          "social"),
            ("A deadline that should have killed us",       "mission"),
            ("Solving it alone at 2am",                     "home")]),
         ("The team is:", [
            ("Small and loyal",                             "rocky"),
            ("Growing fast, energy high",                   "wolf"),
            ("Talented and a bit complicated",              "social"),
            ("Whoever is needed for this one",              "mission"),
            ("Me",                                          "home")]),
         ("What keeps you up:", [
            ("Proving they were wrong about me",            "rocky"),
            ("Keeping the run going",                       "wolf"),
            ("Whether we are building the right thing",     "social"),
            ("The date in the calendar",                    "mission"),
            ("Everything, because it is all mine",          "home")]),
         ("How does the third act go?", [
            ("I go the distance either way",                "rocky"),
            ("Enormous, one way or the other",              "wolf"),
            ("It works, and it changes who is in it",       "social"),
            ("Down to the last second",                     "mission"),
            ("I answer the door and let someone in",        "home")])]))

    # ---- 4. the grant -----------------------------------------------------
    made.append(build(
        "hundred-k", "You just got $100,000. First move?",
        "5 questions, about 30 seconds",
        "No strings, no investor, no board. What you reach for first says more "
        "than any plan you have written down.",
        "I would spend it on", "Five questions and where the money would actually go.",
        "#4FA96B",
        [("marketing","Straight into marketing","#E0483C","You believe the thing works, nobody knows it exists.",
          "Your instinct is that the problem is attention rather than product, and you are often right about that.",
          "Paid attention stops the day the money does."),
         ("hire","Hire someone","#6FA8C4","You are the bottleneck and you know it.",
          "The honest answer is that everything waits on you, and buying hands is the fastest way to stop that.",
          "Hiring while it is chaotic multiplies the chaos rather than dividing it."),
         ("product","Build the product out","#D4A856","Make it good enough to sell itself.",
          "You want to close the gap between what it is and what you promised, and you would rather do that before selling harder.",
          "There is no version so good that it markets itself."),
         ("save","Save nearly all of it","#5FA98C","Runway is the only real strategy.",
          "Cash in the bank buys time, and time is what kills most of the businesses that die.",
          "Runway with nothing changing on it is just a slower ending."),
         ("office","Something you will regret","#7B5CC4","Honest, at least.",
          "The office, the rebrand, the setup. Everyone has one of these, and most people will not admit to it.",
          "You will explain this purchase to somebody in about eight months.")],
        [("What is most broken today?", [
            ("Nobody has heard of us",                      "marketing"),
            ("Everything waits on me",                      "hire"),
            ("The product is not there yet",                "product"),
            ("We are too close to the edge",                "save"),
            ("Honestly, morale",                            "office")]),
         ("A customer says no. The usual reason:", [
            ("They had never heard of us",                  "marketing"),
            ("We were too slow to respond",                 "hire"),
            ("It did not do the thing they needed",         "product"),
            ("Price",                                       "save"),
            ("We did not look established enough",          "office")]),
         ("Money makes you feel:", [
            ("Impatient to use it",                         "marketing"),
            ("Like I can finally delegate",                 "hire"),
            ("Like I can finally finish it",                "product"),
            ("Calm, for the first time in months",          "save"),
            ("Like celebrating",                            "office")]),
         ("Twelve months out, success looks like:", [
            ("Everyone in the category knows us",           "marketing"),
            ("It runs without me in the room",              "hire"),
            ("The thing is genuinely finished",             "product"),
            ("Still here, on our own money",                "save"),
            ("It feels like a real company",                "office")]),
         ("The advice you would ignore:", [
            ("Wait until the product is ready",             "marketing"),
            ("Do it yourself for another year",             "hire"),
            ("Ship it rough and fix it later",              "product"),
            ("Spend it to grow faster",                     "save"),
            ("Be sensible",                                 "office")])]))


    # ---- 5. superpower ----------------------------------------------------
    made.append(build(
        "superpower", "Which founder superpower would you pick?",
        "5 questions, about 30 seconds",
        "You only get one. What you reach for says which part of this you find "
        "hardest, which is more interesting than the power itself.",
        "I would pick", "Five questions and the power you would actually choose.",
        "#7B5CC4",
        [("mindread","Read your customers minds","#6FA8C4","You want to stop guessing.",
          "The part you find hardest is not building, it is knowing what to build. You would trade a lot to skip the guessing.",
          "You would stop asking people things, and asking is how you learn to read them without a power."),
         ("energy","Unlimited energy","#E0483C","You want the day to be longer.",
          "You know exactly what to do. There is simply more of it than there are hours, and that is the whole problem.",
          "Unlimited energy would let you keep doing the wrong thing for much longer."),
         ("fearless","Never fear failure","#D4A856","You want the hesitation gone.",
          "You have known the right move before and not made it. The gap between knowing and doing is where your time goes.",
          "A little fear is the thing that makes you check the numbers first."),
         ("predict","See market trends coming","#5FA98C","You want to stop being surprised.",
          "You would rather be early than fast. Being caught out by something you could have seen is the one that stings.",
          "Knowing what is coming and acting on it are different skills."),
         ("clone","Clone yourself","#C4534A","You want to stop being the bottleneck.",
          "Nothing moves without you. You would rather duplicate the standard than explain it.",
          "A clone is delegation for people who do not want to teach.")],
        [("The most frustrating part of last month:", [
            ("Building the wrong thing",                    "mindread"),
            ("Running out of hours",                        "energy"),
            ("Sitting on a decision too long",              "fearless"),
            ("Getting blindsided",                          "predict"),
            ("Being the only one who could do it",          "clone")]),
         ("When you are stuck, you usually:", [
            ("Go and ask people",                           "mindread"),
            ("Work later",                                  "energy"),
            ("Wait until it feels safer",                   "fearless"),
            ("Read everything about it",                    "predict"),
            ("Do it myself, again",                         "clone")]),
         ("What would you delegate first?", [
            ("Nothing. I need to hear it directly",         "mindread"),
            ("Anything, I just need the hours",             "energy"),
            ("The decisions I keep avoiding",               "fearless"),
            ("Watching the market",                         "predict"),
            ("Everything, if it were done my way",          "clone")]),
         ("The compliment that lands hardest:", [
            ("You really understood what I needed",         "mindread"),
            ("I do not know how you do it all",             "energy"),
            ("You just went for it",                        "fearless"),
            ("You called that months ago",                  "predict"),
            ("Nothing works without you",                   "clone")]),
         ("Your version of a nightmare:", [
            ("Building for a year, nobody wants it",        "mindread"),
            ("Falling behind and not catching up",          "energy"),
            ("Watching someone else do the thing I hesitated on", "fearless"),
            ("The market moves and I am the last to know",  "predict"),
            ("Being off for a week and it all stops",       "clone")])]))

    # ---- 6. if it ran itself ---------------------------------------------
    made.append(build(
        "ran-itself", "If it could run itself tomorrow, what would you do?",
        "5 questions, about 30 seconds",
        "Be honest. This is the question that finds out whether you want the "
        "business or the working.",
        "I would", "Five questions and what you would actually do with the time.",
        "#5FA98C",
        [("travel","Travel","#6FA8C4","You have been saving it up.",
          "There is a list and it is long and it has not moved in years. You have been treating rest as something you earn afterwards.",
          "Afterwards keeps moving. It has moved twice since you started."),
         ("another","Start another one","#E0483C","It was never about this business.",
          "You like the beginning. The bit where it is a blank page and anything is still possible.",
          "Beginnings are the only bit you are practised at, which is why nothing gets to year five."),
         ("sleep","Sleep","#7B5CC4","That is not a joke answer.",
          "You are running a deficit and you know it. The honest answer to what you want is not ambitious, it is horizontal.",
          "Tired is not a personality and it is not a strategy either."),
         ("volunteer","Give the time away","#4FA96B","The business was always the means.",
          "You want the freedom to be useful somewhere that does not pay, which is a good reason to have built the thing.",
          "You put this off exactly as long as you put off rest."),
         ("nothing","Nothing, for six months","#8A8272","And you would not feel guilty.",
          "You have earned the right to stop and you know that you would take it. That is rarer and healthier than it sounds.",
          "Six months of nothing is where people find out what they actually miss.")],
        [("The last real break you took:", [
            ("Booked, then cancelled",                      "travel"),
            ("I started something instead",                 "another"),
            ("I cannot remember",                           "sleep"),
            ("I spent it helping someone else",             "volunteer"),
            ("A while ago, and it was good",                "nothing")]),
         ("A completely open Saturday:", [
            ("Somewhere I have not been",                   "travel"),
            ("Sketching the next idea",                     "another"),
            ("Horizontal",                                  "sleep"),
            ("Something for someone else",                  "volunteer"),
            ("Genuinely nothing",                           "nothing")]),
         ("What do you miss most?", [
            ("Being somewhere else",                        "travel"),
            ("The first month of anything",                 "another"),
            ("Waking up without an alarm",                  "sleep"),
            ("Being useful without invoicing",              "volunteer"),
            ("Not being needed",                            "nothing")]),
         ("If someone gave you a year, paid:", [
            ("I would go and keep going",                   "travel"),
            ("I would build something",                     "another"),
            ("The first month would be a blur",             "sleep"),
            ("I would find work that matters",              "volunteer"),
            ("I would stop and see what happens",           "nothing")]),
         ("The reason you have not already:", [
            ("It never feels like the right month",         "travel"),
            ("I keep starting things instead",              "another"),
            ("There is always one more thing",              "sleep"),
            ("It feels indulgent",                          "volunteer"),
            ("I would not know who I was",                  "nothing")])]))


    # ---- 7. squad ---------------------------------------------------------
    made.append(build(
        "your-squad", "Which SideKix squad would you join?",
        "5 questions, about 30 seconds",
        "Everyone is a bit of all five. One of them is where you would sit down "
        "first and stay longest.",
        "My squad is", "Five questions and the table you would sit at.",
        "#D4A856",
        [("builders","The Builders","#D4A856","You would rather show it than describe it.",
          "The fastest route to your point is a working version of it. You have ended more arguments with a demo than with a paragraph.",
          "Not everything that needed discussing got discussed."),
         ("dreamers","The Dreamers","#7B5CC4","You can see it finished already.",
          "You hold the picture of what this becomes, which is the thing that keeps everyone going on a bad month.",
          "The gap between the picture and Tuesday is where people get discouraged."),
         ("hustlers","The Hustlers","#E0483C","You would rather move than meet.",
          "Ten conversations, four follow ups, and something happened today. You measure a week by what changed in it.",
          "Motion looks like progress right up until it does not."),
         ("strategists","The Strategists","#6FA8C4","You want to know why before how.",
          "You are the person who asks the question that reframes the whole thing, usually twenty minutes in.",
          "The question sometimes arrives after everyone has already committed."),
         ("champions","The Community Champions","#4FA96B","You build the room, not just the thing.",
          "You know who should meet whom, and you make it happen without being asked. The network is the asset.",
          "You give away more time than you count, and nobody sends an invoice for it.")],
        [("A new group forms. Within a week you are:", [
            ("Building the first version",                  "builders"),
            ("Describing where it goes",                    "dreamers"),
            ("Talking to people outside it",                 "hustlers"),
            ("Asking what we are actually solving",         "strategists"),
            ("Introducing everyone properly",               "champions")]),
         ("Which meeting do you want to be in?", [
            ("The one with a prototype on the table",       "builders"),
            ("The one about five years out",                "dreamers"),
            ("The one with a customer in it",               "hustlers"),
            ("The one where we choose between two paths",   "strategists"),
            ("The one where people meet each other",        "champions")]),
         ("Somebody is stuck. You:", [
            ("Sit down and build it with them",             "builders"),
            ("Remind them what it is for",                  "dreamers"),
            ("Find them the person who unblocks it",        "hustlers"),
            ("Work out whether it is worth doing at all",   "strategists"),
            ("Check how they are, first",                   "champions")]),
         ("Your unfair advantage is:", [
            ("I can make the thing",                        "builders"),
            ("I can see it before it exists",               "dreamers"),
            ("I will ask anyone for anything",              "hustlers"),
            ("I see the second order effects",              "strategists"),
            ("I know everybody",                            "champions")]),
         ("Which compliment would you keep?", [
            ("You built that?",                             "builders"),
            ("You made me believe it was possible",         "dreamers"),
            ("You made it happen",                          "hustlers"),
            ("You saw what nobody else did",                "strategists"),
            ("You brought us together",                     "champions")])]))

    # ---- 8. founder confessions -------------------------------------------
    made.append(build(
        "founder-confessions", "What is the most founder thing you have done?",
        "5 questions, about 30 seconds",
        "No judgement. Everyone reading this has done at least three of them.",
        "My confession is", "Five questions and the thing you would rather not admit to.",
        "#C4534A",
        [("vacation","Worked through a holiday","#6FA8C4","You took the laptop. Of course you did.",
          "The trip happened around the work rather than instead of it, and you told yourself it was only an hour a day.",
          "The people who came with you noticed, and did not say."),
         ("domain","Bought a domain at 2am","#7B5CC4","It is still renewing.",
          "The idea was excellent at 2am and it is possible it still is. You own the address either way.",
          "There are eleven of these and one of them was actually good."),
         ("rename","Changed the name five times","#D4A856","The sixth one is the right one.",
          "You have redone the wordmark more often than you have talked to customers about it, and you know how that sounds.",
          "Nobody outside your head noticed any of the five."),
         ("logo","Made the logo before the business","#E0483C","It looked so real.",
          "Having something to point at made it feel like it existed, and that feeling got you through the first month.",
          "A logo is the cheapest way to feel like you started."),
         ("three","Started three at once","#4FA96B","One of them is going to work.",
          "You would rather have three half chances than one full one, and you are genuinely faster than most people at all three.",
          "Three at forty percent is not the same as one at a hundred and twenty.")],
        [("Your browser right now:", [
            ("Work tabs, on a day off",                     "vacation"),
            ("A registrar, mid checkout",                   "domain"),
            ("A font site",                                 "rename"),
            ("A logo tool",                                 "logo"),
            ("Three projects in three windows",             "three")]),
         ("The purchase you would quietly take back:", [
            ("Roaming data to keep working",                "vacation"),
            ("Domains",                                     "domain"),
            ("A rebrand nobody asked for",                  "rename"),
            ("A designer, before revenue",                  "logo"),
            ("Tools for all three of them",                 "three")]),
         ("A friend asks what you do. You:", [
            ("Answer while checking my phone",              "vacation"),
            ("Describe something not built yet",            "domain"),
            ("Use a name they have not heard before",       "rename"),
            ("Show them the logo",                          "logo"),
            ("Ask which one they mean",                     "three")]),
         ("The most recent 11pm decision:", [
            ("To answer one more email",                    "vacation"),
            ("To buy the .co as well",                      "domain"),
            ("That the name was wrong again",               "rename"),
            ("To move the wordmark two pixels",             "logo"),
            ("To begin a fourth thing",                     "three")]),
         ("What would your partner say?", [
            ("You said you were taking a break",            "vacation"),
            ("Another one?",                                "domain"),
            ("What is it called this week",                 "rename"),
            ("It looks great, what does it do",             "logo"),
            ("Which one are we talking about",              "three")])]))


    # ---- 9. pizza ---------------------------------------------------------
    made.append(build(
        "business-pizza", "Your business is a pizza. What is the topping?",
        "5 questions, about 30 seconds",
        "It is a silly question that gets an honest answer, which is the whole "
        "trick of a good one.",
        "My business is", "Five questions and the topping your business has been all along.",
        "#E0483C",
        [("pepperoni","Pepperoni","#C4534A","Traditional, and it works.",
          "You are doing a known thing properly. There is no mystery to explain and no education to fund, which is worth more than founders admit.",
          "Anybody can order the same thing, so the only edge you have is doing it better."),
         ("pineapple","Pineapple","#D9A441","Bold, and people have opinions.",
          "Half the room thinks you are wrong and the other half is extremely loyal. There is no version of this that everyone likes.",
          "You spend real energy defending the choice instead of improving it."),
         ("mushrooms","Mushrooms","#8A7A5C","Quiet, and better than it looks.",
          "You are not the obvious pick and the people who choose you keep choosing you. Word of mouth is doing most of your marketing.",
          "Quiet does not scale on its own. Somebody has to say it out loud."),
         ("everything","Everything on it","#4FA96B","Serial entrepreneur energy.",
          "You said yes to all of it. There is a version of this that is range and a version that is indecision, and only you know which.",
          "Every extra topping makes the thing harder to describe in one sentence.")],
        [("Explain your business in one sentence.", [
            ("Easy. People already know what it is",        "pepperoni"),
            ("I can, but people argue with it",             "pineapple"),
            ("It takes me two sentences, honestly",         "mushrooms"),
            ("I have never managed it in one",              "everything")]),
         ("Your customers found you because:", [
            ("They were already looking for it",            "pepperoni"),
            ("Somebody told them it was mad",               "pineapple"),
            ("Someone they trust recommended it",           "mushrooms"),
            ("Different ones, different reasons",           "everything")]),
         ("What do people say when you describe it?", [
            ("Makes sense",                                 "pepperoni"),
            ("Really?",                                     "pineapple"),
            ("Oh, that is clever",                          "mushrooms"),
            ("So which part is the business?",              "everything")]),
         ("Your competitors:", [
            ("Plenty, and I know them all",                 "pepperoni"),
            ("Almost none, which worries me slightly",      "pineapple"),
            ("A few, quiet like me",                        "mushrooms"),
            ("Different ones for each thing",               "everything")]),
         ("What would you never change?", [
            ("Doing the basics properly",                   "pepperoni"),
            ("The thing people find strange",               "pineapple"),
            ("The quality nobody sees",                     "mushrooms"),
            ("Being able to say yes",                       "everything")])]))

    # ---- 10. shopping cart -------------------------------------------------
    made.append(build(
        "shopping-cart", "What is in your founder shopping cart?",
        "5 questions, about 30 seconds",
        "Where the money goes when nobody is watching. Everyone has a category "
        "and nobody picks it on purpose.",
        "My cart is full of", "Five questions and where your money quietly goes.",
        "#6FA8C4",
        [("books","Books","#8A7A5C","Bought, stacked, mostly unread.",
          "You buy the answer in advance and get to it later. The pile is a to do list you paid for.",
          "Reading about it has started to feel like doing it."),
         ("ai","AI tools","#7B5CC4","A subscription for every problem.",
          "There is a tool for this and you have it. Possibly two, because the second one had a better demo.",
          "Nobody has ever cancelled the first one."),
         ("supplies","Office supplies","#5FA98C","The setup has to be right first.",
          "The desk, the chair, the notebook that is finally the correct notebook. Getting ready is a real feeling and you like it.",
          "Getting ready is not the same as starting, and it is more fun."),
         ("courses","Courses","#D4A856","Module three, every time.",
          "You buy the structured version because structure is the bit you find hardest to make yourself.",
          "The completion rate is the number worth looking at."),
         ("domains","Domain names","#E0483C","Eleven of them. Two are good.",
          "Each one was a real idea at the moment you bought it. The renewals arrive together every year like a report card.",
          "Owning the address is the cheapest possible version of starting.")],
        [("Last thing you bought for the business:", [
            ("Something to read",                           "books"),
            ("A subscription",                              "ai"),
            ("Something for the desk",                      "supplies"),
            ("A course",                                    "courses"),
            ("A domain",                                    "domains")]),
         ("When you feel stuck, you:", [
            ("Find the book on it",                         "books"),
            ("Find the tool for it",                        "ai"),
            ("Tidy, then start",                            "supplies"),
            ("Sign up to learn it properly",                "courses"),
            ("Start a different idea",                      "domains")]),
         ("What is unopened right now?", [
            ("Three books",                                 "books"),
            ("Two trials I forgot to cancel",               "ai"),
            ("A notebook too nice to use",                  "supplies"),
            ("Module three onwards",                        "courses"),
            ("Nine domains",                                "domains")]),
         ("Your monthly spend surprise:", [
            ("How much I spend on reading",                 "books"),
            ("The number of subscriptions",                 "ai"),
            ("How much the setup cost",                     "supplies"),
            ("What I paid to learn things",                 "courses"),
            ("The renewals, all at once",                   "domains")]),
         ("Which would you defend hardest?", [
            ("Every book earned its place",                 "books"),
            ("The tools genuinely save time",               "ai"),
            ("Good tools are not vanity",                   "supplies"),
            ("I finished the ones that mattered",           "courses"),
            ("One of them is going to be worth it",         "domains")])]))

    # ---- 11. the dating profile -------------------------------------------
    made.append(build(
        "dating-profile", "If your business had a dating profile...",
        "5 questions, about 30 seconds",
        "What the bio would say, if it were being honest on a Sunday night.",
        "My bio would say", "Five questions and the bio your business would actually write.",
        "#DE5FA0",
        [("complicated","It is complicated","#7B5CC4","True, and you would still swipe.",
          "Some months it is the best thing you have done and some months you would hand it to anybody. Both are true at once.",
          "Complicated is only a problem when you stop being honest about which month it is."),
         ("longterm","Looking for long term","#4FA96B","You are building something to keep.",
          "You are not in this for the exit and you have turned down the fast version at least once.",
          "Patience and avoidance look identical from the outside."),
         ("heartbreak","Will break your heart, then make you stronger","#C4534A","You have been through it.",
          "You have already survived the version of this that ends everything, and you are still here, changed.",
          "You have started to wear the scar tissue as the qualification."),
         ("available","Available 24/7","#E0483C","Which is not the flex you think.",
          "You answer at midnight and on holiday, and it is genuinely part of why customers stay.",
          "The thing that made you loved is the thing that will make you leave."),
         ("unstable","Financially unstable, emotionally rewarding","#D4A856","Painfully accurate.",
          "The money is not the reason and it is a good job too. You would find it hard to explain to anyone doing this for money.",
          "Rewarding does not pay a bill and it never has.")],
        [("How would last month describe it?", [
            ("Up and down, hourly",                         "complicated"),
            ("Slow and fine",                               "longterm"),
            ("Recovering",                                  "heartbreak"),
            ("Constant",                                    "available"),
            ("Broke, but good",                             "unstable")]),
         ("What would a customer say about you?", [
            ("Hard to pin down",                            "complicated"),
            ("Still here after all these years",            "longterm"),
            ("They came back stronger",                     "heartbreak"),
            ("They always answer",                          "available"),
            ("They really care about this",                 "unstable")]),
         ("Your relationship with the business is:", [
            ("On and off, and I am fine with that",         "complicated"),
            ("Committed, boringly",                         "longterm"),
            ("Repaired",                                    "heartbreak"),
            ("Codependent, if I am honest",                 "available"),
            ("Love, mostly",                                "unstable")]),
         ("The red flag you would admit to:", [
            ("I change my mind",                            "complicated"),
            ("I am slow to move",                           "longterm"),
            ("I bring up the past",                         "heartbreak"),
            ("I do not switch off",                         "available"),
            ("I do not check the balance",                  "unstable")]),
         ("What are you actually looking for?", [
            ("Something that makes sense",                  "complicated"),
            ("Something that lasts",                        "longterm"),
            ("Something worth the last one",                "heartbreak"),
            ("Someone to share the load",                   "available"),
            ("Something that means something",              "unstable")])]))

    return made


if __name__ == "__main__":
    print("wrote:", ", ".join(main()))
