save("save/bookmark", "Book1/523.js");

const MARK = 0;
const GOTO = 1;
const text = [
MARK,
`

  If you have the codeword
Assassin,`,
GOTO,
"Book1/27.js",
`go to 27`,
`immediately. If
not, if you have the title
Protector of Sokara, you are sent
in to see the provost marshal
immediately -`,
GOTO,
"Book1/95.js",
`go to 95`,
`.

  Otherwise, you have to wait
several hours to be seen by one of
the provost marshal's aides, a
certain Captain Royzer.

  If you have the codeword Artery,
Royzer sends you in to see Marloes
Marlock immediately -`,
GOTO,
"Book1/456.js",
`go to 456`,
`.

  Otherwise, you will have to
convince the captain it is worth`,
MARK,
`his while to let you see the
provost marshal. If you are a
Warrior, Rogue or Troubadour,
Royzer will let you in for the
modest bribe of 5 Shards - turn to
* 191 *`,
GOTO,
"Book1/191.js",
`go to 191`,
`.

  If you are a Wayfarer, Priest or
Mage, you will have to convince
the captain of your loyalty to
Sokara first.`,
GOTO,
"Book1/extra_198.js",
`Make a CHARISMA roll
at a difficulty of 9`,
`. If you are
successful, you can then bribe him
- pay 5 Shards and turn to 191 .

  If you fail your CHARISMA roll or
do not wish to pay the bribe,
Captain Royzer dismisses you
rudely.`,
GOTO,
"Book1/10.js",
`go to 10`,
`.`,
MARK
];

const funcs = new Array(5);
funcs[MARK] = f_mark;
funcs[GOTO] = f_goto;

window(0, 0, 220, 176);
io("FILLER", 3, "TEXT", "5x7");
io("FORMAT", 0, 0);

var index, selection = 0;
var position = 1, mark = 0;
var isLastMark = false;



render();

function f_mark(){
    position = index + 1;
    mark = index;
}

function f_goto(trigger){
    var page = text[index + 1];
    var caption = text[index + 2];
    var selected = ((index - mark) == selection);
    if(selected) print("[");
    else print(" ");
    print(caption);
    if(selected) print("]");
    else print(" ");

    index += 2;

    if(trigger){
        position = -1;
        splash(0, 0, "splash.565");
        window(0, 166, 220, 176);
        io("CLEARTEXT");
        cursor(1, 21);
        print(caption);
        exec(page);
    }
}

function isText(i){
    var line = text[i];
    return line < 0 || line >= length(funcs);
}

function render(){
    if(position < 0)
        return;
    io("CLEARTEXT");
    fill(0);
    cursor(0,0);
    color(32);
    index = position;
    for(; text[index] != MARK; ++index){
        var line = text[index];
        if(isText(index)) print(line);
        else funcs[line](false);
    }
    isLastMark = index == length(text) - 1;
    color(7);
}

function update(){
    if(justPressed("C"))
        exit();

    if(justPressed("A")){
        index = mark + selection;
        funcs[text[index]](true);
        render();
    }

    if(!isLastMark){
        flip(true);
        sprite(220-8, 176-8, builtin("cursor2"));
    }

    var direction = justPressed("DOWN") - justPressed("UP");
    if(direction == 0){
        return;
    }
    var prevPrev = 0;
    var prevMark = 0;
    var prevSelection = -1;
    var curSelection = -1;
    var absSelection = mark + selection + (direction > 0);
    index = (mark + selection) * (direction > 0);
    for( ; (prevSelection != absSelection) && (isText(curSelection) || curSelection < absSelection); ++index){
        if(index >= length(text)) return;
        if(isText(index)) continue;
        prevSelection = curSelection;
        curSelection = index;
        var line = text[index];
        if(line != MARK){
            funcs[line](false);
        } else {
            prevPrev = prevMark;
            prevMark = index;
        }
    }

    if(direction > 0){
        index = curSelection;
    }else{
        if(prevSelection < mark){
            if(mark == 0)
                return;
            index = prevPrev;
            funcs[MARK](false);
        }
        index = prevSelection;
    }

    if(text[index] == MARK){
        if(isLastMark && direction > 0){
            render();
            return;
        }
        selection = 0;
    }else
        selection = index - mark;

    funcs[text[index]](false);

    render();
}
