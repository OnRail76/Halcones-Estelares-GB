/* Six original flight patterns inspired by early fixed-screen arcades.
   Positions stay within the DMG playfield. Logic remains at 25 ticks/s. */
#define FORMATION 0
#define DIVE 1
#define FEINT 2
#define RETURNING 3
#define WAIT_ENTRY 4
#define ENTERING 5
#define LAUNCH_WAIT 6
uint8_t home_x[10],home_y[10],hunt_target[10],flight_clock[10],flight_side[10];
uint8_t formation_drift,hunter_active,hunter_solo,wave_rng,launch_serial;
uint8_t pattern_id;
const int8_t wave_sine[64]={0,1,2,3,4,4,5,6,6,7,8,8,9,9,9,9,9,9,9,9,9,8,8,7,6,6,5,4,4,3,2,1,0,-1,-2,-3,-4,-4,-5,-6,-6,-7,-8,-8,-9,-9,-9,-9,-9,-9,-9,-9,-9,-8,-8,-7,-6,-6,-5,-4,-4,-3,-2,-1};
uint8_t approach(uint8_t value,uint8_t target,uint8_t speed){
 if(value<target)return target-value>speed?value+speed:target;
 return value-target>speed?value-speed:target;
}
uint8_t flight_x(int16_t x){uint8_t right=wave<3?102:94;if(x<2)return 2;if(x>right)return right;return x;}
uint8_t flight_random(void){wave_rng^=wave_rng<<3;wave_rng^=wave_rng>>5;wave_rng^=wave_rng<<1;return wave_rng;}
void waves_setup(void){uint8_t i;formation_drift=0;hunter_active=0;hunter_solo=0;attack_pair=0;attack_cd=32;launch_serial=0;
 wave_rng=(uint8_t)sys_time^(phase*17)^(wave*29);if(!wave_rng)wave_rng=0x5d;
 pattern_id=1+flight_random()%6;
 for(i=0;i<10;i++){
  home_x[i]=wave<3?12+(i%5)*19:14+(i%3)*30;home_y[i]=12+(i/(wave<3?5:3))*24;
  flight_clock[i]=i*3;flight_side[i]=i&1;hunt_target[i]=home_x[i];
  foes[i].x=(i&1)?102:2;foes[i].y=0;foes[i].mode=WAIT_ENTRY;
 }
}
void launch_flight(uint8_t i,int8_t offset){
 foes[i].mode=DIVE;flight_clock[i]=0;flight_side[i]=(launch_serial+i)&1;
 hunt_target[i]=flight_x((int16_t)px+4+offset);
}
void waves_move(void){uint8_t i,n=wave<3?10:6,active=0,ready=0,alive=0,limit,group,start,launched=0;
 uint8_t difficulty=phase>5?4:phase-1,gap,home;int16_t target;
 if((ticks&63)==0 && formation_drift<24)formation_drift++;
 for(i=0;i<n;i++)if(foes[i].live){Enemy *e=&foes[i];alive++;home=home_y[i]+formation_drift;
  if(e->mode==WAIT_ENTRY){if(flight_clock[i])flight_clock[i]--;else{e->mode=ENTERING;flight_clock[i]=0;}continue;}
  if(e->mode==ENTERING){
   flight_clock[i]++;target=home_x[i];
   if(flight_clock[i]<24)target+=wave_sine[(flight_clock[i]*2+(flight_side[i]?32:0))&63];
   e->x=approach(e->x,flight_x(target),3);e->y=approach(e->y,home,2);
   if(flight_clock[i]>=24 && e->x==home_x[i] && e->y==home){e->mode=FORMATION;flight_clock[i]=0;}
   continue;
  }
  if(e->mode==FORMATION){
   target=home_x[i]+wave_sine[((ticks>>1)+(pattern_id==4?i*9:0))&63];e->x=flight_x(target);e->y=home;
   if(pattern_id==4)e->y=home+10+wave_sine[((ticks>>1)+i*13)&63];
   ready++;continue;
  }
  active++;
  if(e->mode==RETURNING){
   target=e->y>home+18?(flight_side[i]?94:2):home_x[i];
   e->x=approach(e->x,flight_x(target),3);e->y=approach(e->y,home,3);
   if(e->y==home && e->x==home_x[i]){e->mode=FORMATION;flight_clock[i]=0;}
   continue;
  }
  if(e->mode==LAUNCH_WAIT){if(flight_clock[i])flight_clock[i]--;else e->mode=DIVE;continue;}
  if(e->mode==FEINT){
   if(++flight_clock[i]>=10){e->mode=DIVE;flight_clock[i]=19;hunt_target[i]=flight_x(px+4);fire_enemy(e->x+8,e->y+14);}
   continue;
  }
  flight_clock[i]++;
  if((pattern_id==3 && flight_clock[i]==18)||(pattern_id==4 && flight_clock[i]==12)){e->mode=FEINT;flight_clock[i]=0;continue;}
  if(pattern_id==6 && flight_clock[i]==10)hunt_target[i]=flight_x(px+4);
  target=hunt_target[i];
  if(pattern_id==1)target+=wave_sine[(flight_clock[i]*2+(flight_side[i]?32:0))&63];
  if(pattern_id==2||pattern_id==5)target+=wave_sine[(flight_clock[i]*3+(flight_side[i]?32:0))&63]*2;
  if(pattern_id==4)target+=wave_sine[(ticks*3+i*9)&63];
  if(pattern_id==6)target+=wave_sine[(flight_clock[i]*3+i*11)&63]*3;
  if(e->y<88||pattern_id==6)e->x=approach(e->x,flight_x(target),wave<3?2:3);
  e->y+=2+(wave<3?(flight_clock[i]&1):(difficulty>=2 && (ticks&1)));
  if(flight_clock[i]==14 && e->y<88)fire_enemy(e->x+(wave<3?4:8),e->y+(wave<3?8:14));
  if(e->y>=130)e->mode=RETURNING;
 }
 hunter_active=active;
 if(attack_cd)attack_cd--;
 if(!ready||attack_cd)return;
 limit=pattern_id==1||pattern_id==3?2:(pattern_id==6?4:3);
 group=pattern_id==2||pattern_id==3?2:(pattern_id==5?3:1);
 gap=pattern_id==1?32:(pattern_id==2?34:(pattern_id==3?44:(pattern_id==4?24:(pattern_id==5?52:16))));
 gap-=difficulty*2;if(alive<=3)gap>>=1;if(gap<8)gap=8;
 if(active>=limit)return;
 start=flight_random();while(start>=n)start-=n;
 for(i=0;i<n && launched<group && active<limit;i++){
  uint8_t slot=start+i;if(slot>=n)slot-=n;
  if(foes[slot].live && foes[slot].mode==FORMATION){
   launch_flight(slot,group==1?0:(launched==0?-12:(launched==1?12:0)));if(launched){foes[slot].mode=LAUNCH_WAIT;flight_clock[slot]=launched*6;}launched++;active++;
  }
 }
 if(launched){launch_serial++;attack_cd=gap;}else attack_cd=8;
}
