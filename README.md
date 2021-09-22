# lua-to-cpp
Useful utility for creating C++ classes that can have their values loaded from a Lua script file. Supply a YAML with appropriate definitions and a sample Lua file is created and a C++ class is also created, including appropriate code to load the class's values from the Lua script.

**NOTE:** As of September 2021, only the following Lua variable types are supported:
* number - Mapped to C++ `float` type
* string - Mapped to C++ `std::string` type
* boolean - Mapped to C++ `bool` type


### Example Usage
For this example, we want to automatically generate the C++ to load basic
Player information from Lua script files. Let's first look at the YAML file
that will drive this process,
[player.yaml](https://github.com/owenjklan/lua-to-cpp/blob/main/examples/player.yaml) from
the `examples/` directory:
```yaml
# Player class, YAML spec for lua-to-cpp
class:
  cpp_name: "Player"
  lua_table_name: "player"
  properties:
    - name: "maxHealth"
      type: number
      default: 0
    - name: "playerName"
      type: string
      default: "player"
    - name: "hasAmulet"
      type: boolean
      default: false
```

Very little is required. The `class` key must always be the root key.

`cpp_name` becomes the name of the C++ class that we will create. It is
recommended that this use a capital letter for at least the very first letter.

`lua_table_name` will become the name of our Lua table that the C++ loader
method will search for.

`properties` lists the basic elements of our Lua table.

For each element in `properties` the following are required:
* `name`: This becomes the literal name of the member variable in the C++
  class and the table key name in the Lua table
* `type`: Lua type for this value. This mostly affects generated C++ code,
  which will have Lua types mapped as mentioned in the very opening of this
  README file
* `default`: This value will be set as a default in the generated constructor
  for the C++ class. An example Lua file that creates a suitable table will
  also have this value by default. This example Lua file can be edited and the
  results should differ when used with the generated `example` program.

Appropriate C++ header and source files will be created from this YAML
specification. The C++ class will have a loader function that will load and
convert each named property after having loaded and executed our Lua script
file.

As an additional useful convenience, C++ source for an example program that
demonstrates C++ defaults for the generated class and then property values
that are loaded from an example Lua file, will also be created. You also get
a script suitable for compiling said example program.

## Example launch
We've seen the YAML file that drives everything, so let's now "turn the key",
as it were (no refunds for bad puns).

From the root of the `lua-to-cpp` repository, we can run:
```shell
(venv) owen@overkill:~/git/lua-to-cpp$ ./lua-to-cpp.py examples/player.yaml -d output -C
Reading class specification from file: examples/player.yaml
Wrote 1092 bytes to /home/owen/git/lua-to-cpp/output/Player.cpp
Wrote 465 bytes to /home/owen/git/lua-to-cpp/output/Player.hpp
Wrote 127 bytes to /home/owen/git/lua-to-cpp/output/example.lua
Wrote 1063 bytes to /home/owen/git/lua-to-cpp/output/example.cpp
Wrote 72 bytes to /home/owen/git/lua-to-cpp/output/build_example.sh
```
As we can see, all output was put into the directory we specified with the
`-d` (`--output-dir`) command-line option: `output/`

To summarise from the above command output, we have the following files now
in our `output/` directory:
```text
Player.cpp
Player.hpp
example.lua
example.cpp
build_example.sh
```

If we now try running the `build_example.sh` command (you may need to make it
executable, first):
```shell
(venv) owen@overkill:~/git/lua-to-cpp$ cd output/
(venv) owen@overkill:~/git/lua-to-cpp/output$ ./build_example.sh 
(venv) owen@overkill:~/git/lua-to-cpp/output$ ls -lh
total 48K
-rwxrwxr-x 1 owen owen   72 Sep 22 17:34 build_example.sh
-rwxrwxr-x 1 owen owen  23K Sep 22 17:37 example
-rw-rw-r-- 1 owen owen 1.1K Sep 22 17:34 example.cpp
-rw-rw-r-- 1 owen owen  127 Sep 22 17:34 example.lua
-rw-rw-r-- 1 owen owen  465 Sep 22 16:55 Player
-rw-rw-r-- 1 owen owen 1.1K Sep 22 17:34 Player.cpp
-rw-rw-r-- 1 owen owen  465 Sep 22 17:34 Player.hpp
(venv) owen@overkill:~/git/lua-to-cpp/output$ 
```

We now have a new file, `example`. Is it executable?
```shell
(venv) owen@overkill:~/git/lua-to-cpp/output$ file example
example: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ae07c4447a675a0ade84d0276e421af386d53eb7, for GNU/Linux 3.2.0, not stripped
```

Apparently so!

Before continuing, let's take a quick peek at the generated `example.lua` file.
```text
-- Auto-generated by lua-to-cpp
player = {}
player["maxHealth"] = 0
player["playerName"] = "player"
player["hasAmulet"] = false
```

As we can see, we have a new table with a bunch of properties that have been
configured with appropriate defaults based on their type and the defaults set
in the YAML file.

So what happens if we run the `example` program?
```shell
(venv) owen@overkill:~/git/lua-to-cpp/output$ ./example 
Displaying defaults loaded from YAML template in constructor:
maxHealth           : 0
playerName          : player
hasAmulet           : 0
Player::loadFromLuaScript() called.
Displaying class values after load from Lua:
maxHealth           : 0
playerName          : player
hasAmulet           : 0
Example program finished.
```

Excellent! We can see that our defaults have been set correctly by the C++
class's constructor. Let's quickly change the content's of `example.lua` a bit:
```text
-- Auto-generated by lua-to-cpp
-- ... then hand-edited after the fact.
player = {}
player["maxHealth"] = 12
player["playerName"] = "Roger, the Shrubber"
player["hasAmulet"] = true
```

If we re-run the `example` program again, we should now get different results
between the default class settings and what we loaded from our Lua file:
```shell
(venv) owen@overkill:~/git/lua-to-cpp/output$ ./example 
Displaying defaults loaded from YAML template in constructor:
maxHealth           : 0
playerName          : player
hasAmulet           : 0
Player::loadFromLuaScript() called.
Displaying class values after load from Lua:
maxHealth           : 12
playerName          : Roger, the Shrubber
hasAmulet           : 1
Example program finished.
```

There we have it! We've given our player a name, a couple of hit-points and
indicated that they do indeed have the Amulet (no Grail, though).

For completeness-sake, let's take a look at the C++ source file that was
generated (looking at the other files is an exercise for the reader, if they
are so inclined) for our Player class:
```text
#include <iostream>
#include <string>

#include "Player.hpp"

Player::Player() {
    maxHealth = 0.000000f;
    playerName = "player";
    hasAmulet = false;
    
}

Player::~Player() {}

bool Player::loadFromLuaScript(lua_State *L, const char *luaPath) {
    // hi there
    std::cout << "Player::loadFromLuaScript() called." << std::endl;

    // "execute" our config file
    luaL_dofile(L, "example.lua");

    // TODO: Add success check!!

    // Setup table access
    lua_getglobal(L, "player");
    if (lua_istable(L, -1)) {
        lua_pushstring(L, "maxHealth");
        lua_gettable(L, -2); // lookup our property in table
        maxHealth = lua_tonumber(L, -1);
        
        lua_pop(L, 1);
        lua_pushstring(L, "playerName");
        lua_gettable(L, -2); // lookup our property in table
        playerName = lua_tostring(L, -1);
        
        lua_pop(L, 1);
        lua_pushstring(L, "hasAmulet");
        lua_gettable(L, -2); // lookup our property in table
        hasAmulet = lua_toboolean(L, -1);
        
        lua_pop(L, 1);
        
    }

    return true;
}
```

Oops! Error handling is still somewhat missing. However, as you can see, the
basic principal here is reasonably sound and the tooling is useable.

## Enjoy, folks!