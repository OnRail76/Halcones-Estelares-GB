/* Controls and lasers run every presentation frame, independently of wave AI. */
#define LASER_SPEED 5
uint8_t fire_repeat;
void player_tick(void){uint8_t i,j,slot,speed=1+(sys_time&1),old_y,old_x=px;
 if((pressed&J_B) && !shield_state){CRITICAL {shield_timer=179;shield_state=1;}sfx_start(FX_SHIELD);}
 if(keys&J_LEFT)px=px>4+speed?px-speed:4;
 if(keys&J_RIGHT)px=px+speed<92?px+speed:92;
 ship_tilt=px<old_x?1:(px>old_x?-1:0);
 /* Existing projectiles travel before a newly pressed shot appears at the muzzle. */
 for(i=0;i<2;i++)if(shots[i].live){
  old_y=shots[i].y;
  shots[i].y=old_y>LASER_SPEED?old_y-LASER_SPEED:0;
  if(state==PLAY && wave==7)for(j=0;j<6;j++)if(foes[j].live && shots[i].x>=foes[j].x && shots[i].x<foes[j].x+8 && shots[i].y<foes[j].y+8 && old_y>=foes[j].y){foes[j].live=0;hide_enemy(j);shots[i].live=0;add_score(10);boom(foes[j].x,foes[j].y);break;}
  if(!shots[i].live)continue;
  if(state==PLAY && wave==7 && !moai_intro){
   if(shots[i].x>=MOAI_X && shots[i].x<MOAI_X+MOAI_W && shots[i].y<MOAI_Y+MOAI_H && old_y>=MOAI_Y){
    shots[i].live=0;boss_hp--;moai_damage();add_score(10);sfx_start(FX_HIT);
    if(!boss_hp){clear_shots();state=MOAI_DEATH;moai_death_begin();return;}
   }
  }else if(state==PLAY && wave!=7)for(j=0;j<10;j++)if(foes[j].live && foes[j].mode!=WAIT_ENTRY){
   uint8_t size=foes[j].kind?16:8;
   if(shots[i].x>=foes[j].x && shots[i].x<foes[j].x+size && shots[i].y<foes[j].y+size && old_y>=foes[j].y){
    foes[j].live=0;hide_enemy(j);shots[i].live=0;add_score(10);boom(foes[j].x,foes[j].y);waves_reinforce(j);break;
   }
  }
  if(shots[i].y<4)shots[i].live=0;
 }
 if(fire_repeat)fire_repeat--;
 if(!(keys&J_A) || shield_state==1)fire_repeat=0;
 if(shield_state!=1 && ((pressed&J_A) || ((keys&J_A) && !fire_repeat))){
  fire_repeat=6;
  /* Every new press gets a muzzle flash/laser, even when both slots are busy.
     Reuse the furthest laser instead of silently dropping the input. */
  slot=!shots[0].live?0:(!shots[1].live?1:(shots[0].y<shots[1].y?0:1));
  shots[slot].x=px+8;shots[slot].y=106;shots[slot].live=1;audio_fire_now();
 }
}
void player_display(void){uint8_t i,x=state==DYING?death_x:px,base=52;int8_t tilt=state==DYING?0:ship_tilt;
 if(state==DYING)base=66+(death_timer>24?0:(death_timer>12?12:24));
 for(i=0;i<6;i++){
  if((state==PLAY || state==TRANSITION) && invulnerable && ((120-invulnerable)&8))hide_sprite(ship_oam[i]);
  else{set_sprite_tile(ship_oam[i],base+i*2);move_sprite(ship_oam[i],x+4+(i/2)*8,128+(i%2)*16+(i<2?tilt:(i>=4?-tilt:0)));}
 }
 for(i=0;i<2;i++){set_sprite_tile(8+i,40);if((state==PLAY || state==TRANSITION) && shots[i].live)move_sprite(8+i,shots[i].x+5,shots[i].y+16);else hide_sprite(8+i);}
 if((state==PLAY || state==TRANSITION) && shield_state==1)pair(6,44,px,106);else{hide_sprite(6);hide_sprite(7);}
}
