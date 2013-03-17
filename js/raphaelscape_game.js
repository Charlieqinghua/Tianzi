
/**
 * Copyright (c) 2009, Benjamin Joffe
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE AUTHOR AND CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


var map,
    canvas,
    overlay,
    bigsky,
    bigsky2,
    arena;
//variables initiated at the bottom of the code...

var pi=Math.PI;

var total=0;

var arenaSize=21;

var total=0;

var samples=200;

var playerPos=[3.5,3.5]; // x,y (from top left)
var playerDir=0.4; // theta, facing right=0=2pi
var playerPosZ=1;
var key=[0,0,0,0,0]; // left, right, up, down

var playerVelY=0;


var face=[];

function initArena(arenaWidth,arenaLength) {
    var arena=[];
    for (var i=0; i<arenaWidth; i++) {
        arena[i] = [];
        for (var j=0; j<arenaLength; j++) {
            arena[i][j] = 1;
            if (i==0 || i==(arenaWidth-1)) {arena[i][j]=2;} // east-west borders
            if (j==0 || j==(arenaLength-1)) {arena[i][j]=2;} // north-south borders
        }
    }

    //do the Depth First Search (DFS) maze generation algorithm
    var cellStack = [];
    var totalCells = (arenaLength-1)/2 * (arenaWidth-1)/2;
    var currCell = [3,3]; // must be odd number indices, goes with playerPos
    var currX = currCell[0];
    var currY = currCell[1];
    arena[currX][currY] = 0; //clear the starting cell
    var cellsBeen = 1;
    while (cellsBeen < totalCells) {
        var potentialNextCells = [1,1,1,1]; // all 4 directions (WSEN) are potential to start

        // remove some potential directions
        var currCellVal = getVal(arena,currCell);
        if (currCellVal[0] != 1) { // west border(2) or already been west(0)
            potentialNextCells[0] = 0;
        }
        if (currCellVal[1] != 1) { // south border(2) or already been south(0)
            potentialNextCells[1] = 0;
        }
        if (currCellVal[2] != 1) { // east border(2) or already been east(0)
            potentialNextCells[2] = 0;
        }
        if (currCellVal[3] != 1) { // north border(2) or already been north(0)
            potentialNextCells[3] = 0;
        }

        // pick which way to go from remaining potentials or back up if all potentials were removed
        var potentialSum = potentialNextCells[0]+potentialNextCells[1]+potentialNextCells[2]+potentialNextCells[3];
        if (potentialSum > 0) { // at least one potential
            var pickList = [];
            if (potentialNextCells[0]) { pickList.push("W"); }
            if (potentialNextCells[1]) { pickList.push("S"); }
            if (potentialNextCells[2]) { pickList.push("E"); }
            if (potentialNextCells[3]) { pickList.push("N"); }
            var picked = pickList[Math.floor( Math.random()*pickList.length )];
            switch(picked) {
                case "W" : //go west, knock down walls
                    cellStack.push(currCell);
                    arena[currX-1][currY] = 0; //clear the intermediate point
                    currX = currX - 2;
                    currCell = [currX,currY];
                    arena[currX][currY] = 0; //clear the new cell
                    break;
                case "S" : //go south, knock down walls
                    cellStack.push(currCell);
                    arena[currX][currY+1] = 0; //clear the intermediate point
                    currY = currY + 2;
                    currCell = [currX,currY];
                    arena[currX][currY] = 0; //clear the new cell
                    break;
                case "E" : //go east, knock down walls
                    cellStack.push(currCell);
                    arena[currX+1][currY] = 0; //clear the intermediate point
                    currX = currX + 2;
                    currCell = [currX,currY];
                    arena[currX][currY] = 0; //clear the new cell
                    break;
                case "N" : //go north, knock down walls
                    cellStack.push(currCell);
                    arena[currX][currY-1] = 0; //clear the intermediate point
                    currY = currY - 2;
                    currCell = [currX,currY];
                    arena[currX][currY] = 0; //clear the new cell
                    break;
                default : //now what?
            }
            cellsBeen = cellsBeen + 1;
        } else { // no potentials, then back up
            currCell = cellStack.pop();
            currX = currCell[0];
            currY = currCell[1];
        }
    }

    return arena;
}

function getVal(maze,cell) {
    var neighbors = [];
    var ix = cell[0];
    var iy = cell[1];
    if (maze[ix-1][iy] == 2) { neighbors[0] = 2;  //W
    } else { neighbors[0] = maze[ix-2][iy]; }
    if (maze[ix][iy+1] == 2) { neighbors[1] = 2;  //S
    } else { neighbors[1] = maze[ix][iy+2]; }
    if (maze[ix+1][iy] == 2) { neighbors[2] = 2;  //E
    } else { neighbors[2] = maze[ix+2][iy]; }
    if (maze[ix][iy-1] == 2) { neighbors[3] = 2;  //N
    } else { neighbors[3] = maze[ix][iy-2]; }
    return neighbors;
}

function wallDistance(theta){

    var data=[];
    face=[];

    var x = playerPos[0], y = playerPos[1],
        deltaX, deltaY,
        distX, distY,
        stepX, stepY,
        mapX, mapY;

    var atX=Math.floor(x), atY=Math.floor(y);

    var thisRow=-1;
    var thisSide=-1;

    var lastHeight=0;

    for (var i=0; i<samples; i++) {
        theta+=pi/(3*samples)+2*pi;
        theta%=2*pi;

        mapX = atX;
        mapY = atY;

        deltaX=1/Math.cos(theta);
        deltaY=1/Math.sin(theta);

        if (deltaX>0) {
            stepX = 1;
            distX = (mapX + 1 - x) * deltaX;
        }
        else {
            stepX = -1;
            distX = (x - mapX) * (deltaX*=-1);
        }
        if (deltaY>0) {
            stepY = 1;
            distY = (mapY + 1 - y) * deltaY;
        }
        else {
            stepY = -1;
            distY = (y - mapY) * (deltaY*=-1);
        }


        for (var j=0; j<20; j++) {
            if (distX < distY) {
                mapX += stepX;
                if (arena[mapX][mapY]) {
                    if (thisRow!=mapX || thisSide!=0) {
                        if (i>0) {
                            data.push(i);
                            data.push(lastHeight);
                        }
                        data.push(i);
                        data.push(distX);
                        thisSide=0;
                        thisRow=mapX;
                        face.push(1+stepX);
                    }
                    lastHeight=distX;
                    break;
                }
                distX += deltaX;
            }
            else {
                mapY += stepY;
                if (arena[mapX][mapY]) {
                    if (thisRow!=mapY || thisSide!=1) {
                        if (i>0) {
                            data.push(i);
                            data.push(lastHeight);
                        }
                        data.push(i);
                        data.push(distY);
                        thisSide=1;
                        thisRow=mapY;
                        face.push(2+stepY);
                    }
                    lastHeight=distY;
                    break;
                }
                distY += deltaY;
            }
        }
    }
    data.push(i);
    data.push(lastHeight);

    return data;
}

function drawCanvas(){

    // var i = walls.length;
    // while (i--) walls[i].hide();
    var theta = playerDir-pi/6;

    var wall=wallDistance(theta);

    var linGrad;

    var tl,tr,bl,br;

    var theta1,theta2,fix1,fix2,j = 0,
        mapview = ["M", 8*playerPos[0], 8*playerPos[1], "L"];
    for (var i=0; i<wall.length; i+=4) {

        theta1=playerDir-pi/6 + pi*wall[i]/(3*samples);
        theta2=playerDir-pi/6 + pi*wall[i+2]/(3*samples);

        fix1 = Math.cos(theta1-playerDir);
        fix2 = Math.cos(theta2-playerDir);

        var h=2-playerPosZ;

        var wallH1=100/(wall[i+1]*fix1);
        var wallH2=100/(wall[i+3]*fix2);

        tl=[wall[i]*2 + .001, 150-wallH1*h];
        tr=[wall[i+2]*2 + .001, 150-wallH2*h];
        br=[wall[i+2]*2 + .001, tr[1]+wallH2*2];
        bl=[wall[i]*2 + .001, tl[1]+wallH1*2];

        var shade1=Math.floor(wallH1*2+20); if (shade1>255) shade1=255;
        var shade2=Math.floor(wallH2*2+20); if (shade2>255) shade2=255;

        var c1 = 'rgb('+(face[i/4]%2==0 ? shade1 : 0)+','+(face[i/4]==1 ? shade1 : 0)+','+(face[i/4]==2 ? 0 : shade1)+')';
        var c2 = 'rgb('+(face[i/4]%2==0 ? shade2 : 0)+','+(face[i/4]==1 ? shade2 : 0)+','+(face[i/4]==2 ? 0 : shade2)+')';

        !walls[j] && (walls[j] = canvas.path().attr({stroke: "none", fill: "#000"})).insertBefore(overlay);
        walls[j++].show().attr({
            path: ["M", tl, "L", tr, br, bl],
            fill: "0-" + c1 + "-" + c2
        });
        mapview = mapview.concat([playerPos[0]*8+Math.cos(theta1)*(wall[i+1])*8, playerPos[1]*8+Math.sin(theta1)*(wall[i+1])*8, playerPos[0]*8+Math.cos(theta2)*(wall[i+3])*8, playerPos[1]*8+Math.sin(theta2)*(wall[i+3])*8]);

    }
    if (!mapball) {
        mapball = map.circle(playerPos[0]*8, playerPos[1]*8, 3).attr({fill:"#36c", stroke: "none"});
        maplight = map.path(mapview).attr({fill:"#f00", stroke: "none"});
    } else {
        mapball.attr({
            cx: playerPos[0] * 8,
            cy: playerPos[1] * 8
        });
        maplight.attr({path: mapview});
    }
    while (walls[j]) walls[j++].hide();
}
var mapball, maplight, walls = [];


function nearWall(x,y){
    var xx,yy;
    if (isNaN(x)) x=playerPos[0];
    if (isNaN(y)) y=playerPos[1];
    for (var i=-0.1; i<=0.1; i+=0.2) {
        xx=Math.floor(x+i);
        for (var j=-0.1; j<=0.1; j+=0.2) {
            yy=Math.floor(y+j);
            if (arena[xx][yy]) return true;
        }
    }
    return false;
}

function wobbleGun(){
    var mag=playerVelY;
    overlay.attr({
        x: 10+Math.cos(total/6.23)*mag*90,
        y: 10+Math.cos(total/5)*mag*90
    });
    // document.getElementById("overlay").style.backgroundPosition=(10+Math.cos(total/6.23)*mag*90)+"px "+(10+Math.cos(total/5)*mag*90)+"px";
}


var jumpCycle=0;


function update(){

    total++;

    var change=false;

    if (jumpCycle) {
        jumpCycle--;
        change=true;
        playerPosZ = 1 + jumpCycle*(20-jumpCycle)/110;
    }
    else if (key[4]) jumpCycle=20;

    if (key[0]) {
        if (!key[1]) {
            playerDir-=0.07; //left
            change=true;
        }
    }
    else if (key[1]) {
        playerDir+=0.07; //right
        change=true;
    }

    if (change) {
        playerDir+=2*pi;
        playerDir%=2*pi;
        bigsky.attr({x: 1-playerDir/(2*pi)*2400});
        bigsky2.attr({x: 2399 + 1-playerDir/(2*pi)*2400});
    }

    if (key[2] && !key[3]) {
        if (playerVelY<0.1) playerVelY += 0.02;
    }
    else if (key[3] && !key[2]) {
        if (playerVelY>-0.1) playerVelY -= 0.02;
    }
    else {
        if (playerVelY<-0.02) playerVelY += 0.015;
        else if (playerVelY>0.02) playerVelY -= 0.015;
        else playerVelY=0;
    }


    if (playerVelY!=0) {

        var oldX=playerPos[0];;
        var oldY=playerPos[1];
        var newX=oldX+Math.cos(playerDir)*playerVelY;
        var newY=oldY+Math.sin(playerDir)*playerVelY;

        if (!nearWall(newX, oldY)) {
            playerPos[0]=newX;
            oldX=newX;
            change=true;
        }
        if (!nearWall(oldX, newY)) {
            playerPos[1]=newY;
            change=true;
        }

    }

    if (playerVelY) wobbleGun();
    if (change) drawCanvas();

}


function changeKey(which, to){
    switch (which){
        case 65:case 37: key[0]=to; break; // left
        case 87: case 38: key[2]=to; break; // up
        case 68: case 39: key[1]=to; break; // right
        case 83: case 40: key[3]=to; break;// down
        case 32: key[4]=to; break; // space bar;
        case 17: key[5]=to; break; // ctrl
    }
}
document.onkeydown=function(e){changeKey((e||window.event).keyCode, 1);};
document.onkeyup=function(e){changeKey((e||window.event).keyCode, 0);};


function initUnderMap(){
    var ulen = arena.length;
    var uwid = arena[0].length;
    // var underMap=Raphael(document.getElementById("underMap"),uwid*8,ulen*8);
    map.rect(0,0, uwid*8, ulen*8).attr({fill:"#FFF", stroke:"#fff"});
    for (var i=0; i<uwid; i++) {
        for (var j=0; j<ulen; j++) {
            var i8 = i*8;
            var j8 = j*8;
            if (arena[i][j]==1) { map.rect(i8,j8, 8,8).attr({fill:"#444", stroke:"#444"}); }
            if (arena[i][j]==2) { map.rect(i8,j8, 8,8).attr({fill:"#888", stroke:"#888"}); }
        }
    }
    canvas.rect(0, 150, 400, 150).attr({stroke: "none", fill: "270-#232-#999"});
    bigsky = canvas.image("sky.jpg", 0, 0, 2400, 150);
    bigsky2 = canvas.image("sky.jpg", 0, 0, 2400, 150);
    overlay = canvas.image("overlay.gif", 0, 0, 457, 351);
}

//window.onerror=function(){
//  alert('An error has occured, the most likely reason is because you are using an incompatible browser.\nYou must be using one of the following browsers or a newer version:\n\n- Internet Explorer 6\n- Firefox 1.5\n- Safari 1.3\n- Opera 9');
//  window.onerror=function(){};
//  return true;
//}

window.onload=function(){
    map=Raphael(document.getElementById("map"),210,210);
    canvas=Raphael(document.getElementById("canvas"),400,300);
    arena=initArena(arenaSize,arenaSize); //must be odd numbers > 3 for this style maze
    initUnderMap();
    drawCanvas();
    bigsky.attr({x: -playerDir/(2*pi)*2400});
    bigsky2.attr({x: 2399 - playerDir/(2*pi)*2400});
    setInterval(update, 35);
};
