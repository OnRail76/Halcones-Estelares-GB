/* HALCONES ESTELARES - native DMG adaptation, based on Tony C. Ware's 1.3.3.
   VBlank-timed shield; no Spectrum code is executed on the Game Boy. */
#include <gb/gb.h>
#include <stdint.h>
#include <string.h>
#include "assets.h"
#include "packed.h"
#include "sprites.h"
#define TITLE 0
#define PLAY 1
#define OVER 2
#define VICTORY 3
#define TRANSITION 4
#define DYING 5
#define MOAI_DEATH 6
const char alphabet[]=" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:-.!/";
typedef struct { uint8_t x,y,live,mode,kind; } Enemy;
typedef struct { uint8_t x,y,live; } Shot;
Enemy foes[10]; Shot shots[2], plasma[3];
int8_t plasma_dx[3];
uint8_t plasma_aim[3],plasma_span[3];
uint16_t plasma_error[3];
volatile uint8_t state,paused,shield_state;
uint8_t keys,pressed,px,lives,wave,phase,boss_hp,boss_max_hp;
int8_t ship_tilt;
uint8_t boss_crack1,boss_crack2,boss_crack3;
volatile uint8_t invulnerable;
uint8_t explosion,ex,ey;
uint16_t ticks,state_timer;
volatile uint16_t shield_timer;
uint32_t score,record;
uint8_t life_hits;
uint8_t field[32*18],tmp[32];
uint8_t fire_cd,attack_cd,shooter,attack_pair,rest_ticks;
uint8_t fire_period,plasma_speed;
uint16_t sim_phase,clock_last;
volatile uint8_t death_timer;
uint8_t death_x;
const uint8_t ship_oam[6]={0,1,2,3,4,5};
void player_display(void);
volatile uint8_t input_now,input_previous,input_press;
#include "audio.h"
volatile uint8_t shield_ready;
/* VBlank keeps the shield at 3 s / 6 s even when rendering takes two frames. */
void input_tick(void){uint8_t now=joypad();input_press|=now&~input_previous;input_previous=now;input_now=now;}
void timers(void){
 audio_tick();
 if(state==DYING){if(death_timer)death_timer--;return;}
 if((state!=PLAY && state!=TRANSITION) || paused)return;
 if(invulnerable)invulnerable--;
 if(shield_timer){shield_timer--;if(!shield_timer){
  if(shield_state==1){shield_state=2;shield_timer=358;}else{shield_state=0;shield_ready=1;}
 }}
}
uint8_t glyph(char c) { uint8_t i=0; while(alphabet[i] && alphabet[i]!=c)i++; return alphabet[i]?i:0; }
void text(uint8_t x,uint8_t y,const char *s,uint8_t base) {
 uint8_t n=0; while(*s && n<20-x)tmp[n++]=glyph(*s++)+base;
 set_bkg_tiles(x,y,n,1,tmp);
}
void number(uint8_t *p,uint32_t v,uint8_t count) { while(count){p[--count]=27+v%10;v/=10;} }
void hide_all(void){uint8_t i;for(i=0;i<40;i++)hide_sprite(i);}
void noise(void){sfx_start(FX_COLLAPSE);}
void pair(uint8_t n,uint8_t tile,int16_t x,int16_t y){
 set_sprite_tile(n,tile);set_sprite_tile(n+1,tile+2);
 move_sprite(n,x+8,y+16);move_sprite(n+1,x+16,y+16);
}
void blank(void){uint16_t i; for(i=0;i<576;i++)field[i]=0;set_bkg_tiles(0,0,32,18,field);SCY_REG=0;SCX_REG=0;}
void waves_setup(void);
void waves_seed(void);
void waves_reinforce(uint8_t killed);
void boss_init(void);
void render_fx(void);
void hide_enemy(uint8_t i){hide_sprite(13+i*2);hide_sprite(14+i*2);}
#include "hud.h"
#include "moai.h"
/* Static cosmic art is installed only at scene entry; field restores overlays. */
void space_field(uint8_t cosmic){uint8_t i,x,y,t;
 const uint8_t star[16]={0,0,0,0,0,0,0,0,0x10,0,0,0,0,0,0,0};
 const uint8_t bright[16]={0,0,0,0,0,0,0,0x10,0,0x18,0,0,0,0,0,0};
 const uint8_t star_xy[32]={1,2,10,1,3,5,12,4,0,8,7,6,5,10,11,8,2,13,9,12,6,16,13,15,4,1,8,17,1,17,12,11};
 memset(field,0,sizeof(field));set_bkg_data(48,1,cosmic?bright:star);
 if(cosmic){
  packed_tiles(cosmos_a_rle,236,16,0);
  packed_tiles(cosmos_b_rle,49,16,0);
  /* Galaxy's last tile uses slot 64: blank edge, remapped to blank tile 0
     before the wave banner overwrites that slot. */
  for(y=0;y<4;y++)for(x=0;x<4;x++){
   field[(uint16_t)(y+5)*32+x]=236+y*4+x;
   t=y*4+x;field[(uint16_t)(y+1)*32+10+x]=t==15?0:49+t;
  }
 }
 for(i=0;i<16;i++)if(!field[(uint16_t)star_xy[i*2+1]*32+star_xy[i*2]])field[(uint16_t)star_xy[i*2+1]*32+star_xy[i*2]]=48;
 set_bkg_tiles(0,0,32,18,field);
}
void setup_field(void){
 DISPLAY_OFF;hide_all();load_font(0);space_field(1);
 packed_tiles(waveclear_data_rle,64,WAVECLEAR_COUNT,0);hud_setup();SHOW_BKG;SHOW_SPRITES;
}
void title(void){uint8_t i;DISPLAY_OFF;HIDE_WIN;hide_all();blank();
 packed_tiles(title_data_rle,0,TITLE_COUNT,0);
 unpack(title_map_rle,field,360);set_bkg_tiles(0,0,20,18,field);
 SHOW_BKG;SHOW_SPRITES;oam_commit();DISPLAY_ON;state=TITLE;ticks=0;paused=0;audio_title();
 for(i=0;i<40;i++)set_sprite_prop(i,0);
}
void clear_shots(void){uint8_t i;for(i=0;i<2;i++){shots[i].live=0;hide_sprite(8+i);}for(i=0;i<3;i++){plasma[i].live=0;hide_sprite(10+i);}}
/* Recomputed at wave entry, never divided in the inner combat loop. */
void difficulty_refresh(void){uint8_t base,minimum;uint16_t divisor;
 base=wave<3?70:(wave<5?54:(wave<7?28:42));
 minimum=wave<3?10:(wave<5?8:(wave<7?6:10));
 divisor=256+(uint16_t)(phase-1)*40;
 fire_period=((uint16_t)base<<8)/divisor;
 if(fire_period<minimum)fire_period=minimum;
 plasma_speed=2+(phase>=3)+(phase>=7);
}
void clear_plasma(void){uint8_t i;for(i=0;i<3;i++){plasma[i].live=0;hide_sprite(10+i);}}
void wave_clear_screen(void){clear_plasma();state=TRANSITION;state_timer=60;}
void wave_clear_tick(void){uint8_t row;
 if(state_timer<=44 && state_timer>=34 && !(state_timer&1)){
  row=(44-state_timer)>>1;set_bkg_tiles(0,6+row,14,1,waveclear_map+row*14);
 }else if(state_timer<=12 && state_timer && !(state_timer&1)){
  row=(12-state_timer)>>1;set_bkg_tiles(0,6+row,14,1,field+(uint16_t)(6+row)*32);
 }
 if(state_timer)state_timer--;
}
void victory_screen(void){uint8_t i,next=phase<99?phase+1:99;
 DISPLAY_OFF;HIDE_WIN;hide_all();blank();
 packed_tiles(victory_data_rle,0,VICTORY_COUNT,0);load_font(212);
 unpack(victory_map_rle,field,360);set_bkg_tiles(0,0,20,18,field);
 number(tmp,next,2);for(i=0;i<2;i++)tmp[i]+=212;set_bkg_tiles(9,13,2,1,tmp);
 number(tmp,score,5);for(i=0;i<5;i++)tmp[i]+=212;set_bkg_tiles(11,15,5,1,tmp);
 tmp[0]=212+27+lives;set_bkg_tiles(11,16,1,1,tmp);
 state=VICTORY;state_timer=180;oam_commit();DISPLAY_ON;sfx_start(FX_LIFE);
}
void spawn_wave(void){uint8_t i;
 clear_plasma();for(i=0;i<10;i++)hide_enemy(i);hide_sprite(35);ticks=0;explosion=0;
 hide_sprite(33);hide_sprite(34);audio_wave();
 difficulty_refresh();fire_cd=fire_period;attack_cd=48;shooter=0;attack_pair=0;rest_ticks=0;
 if(wave==7){space_field(0);boss_init();moai_setup();
 }else{waves_setup();}
 if(!(LCDC_REG&0x80)){for(i=0;i<8;i++)update_hud();hud_flush_all();}
 state=PLAY;oam_commit();DISPLAY_ON;
}
void new_game(void){waves_seed();ship_tilt=0;state=TRANSITION;audio_game();death_timer=0;sim_phase=0;px=48;lives=3;wave=1;phase=1;score=0;life_hits=0;shield_state=0;shield_timer=0;invulnerable=120;explosion=0;clear_shots();setup_field();spawn_wave();}
void damage(void){if(state!=PLAY || shield_state==1 || invulnerable)return;
 lives--;death_x=px;death_timer=36;state=DYING;explosion=0;clear_shots();
 hide_sprite(6);hide_sprite(7);hide_sprite(33);hide_sprite(34);sfx_start(FX_DEATH);
}
void respawn(void){uint8_t i;ship_tilt=0;px=48;clear_shots();
 for(i=6;i<=12;i++)hide_sprite(i);hide_sprite(33);hide_sprite(34);
 CRITICAL {invulnerable=120;state=PLAY;input_press=0;}
 sim_phase=0;clock_last=sys_time;
}
void end_screen(void){uint8_t i;audio_over();DISPLAY_OFF;HIDE_WIN;hide_all();blank();
 packed_tiles(gameover_data_rle,0,GAMEOVER_COUNT,0);load_font(212);
 unpack(gameover_map_rle,field,360);set_bkg_tiles(0,0,20,18,field);
 text(2,12,"PUNTOS",212);number(tmp,score,5);for(i=0;i<5;i++)tmp[i]+=212;set_bkg_tiles(11,12,5,1,tmp);
 oam_commit();DISPLAY_ON;state=OVER;state_timer=180;
}
void add_score(uint8_t n){
 if(score<99990UL)score+=n;if(score>99990UL)score=99990UL;
 if(score>record)record=score;
 if(++life_hits==100){life_hits=0;if(lives && lives<3){lives++;sfx_start(FX_LIFE);}}
}
void boom(int16_t x,int16_t y){ex=x;ey=y;explosion=18;sfx_start(FX_EXPLODE);}
uint8_t hit(int16_t x,int16_t y,int16_t x2,int16_t y2,uint8_t w,uint8_t h){return x>=x2 && x<x2+w && y>=y2 && y<y2+h;}
void fire_enemy(int16_t x,int16_t y){uint8_t i;for(i=0;i<3;i++)if(!plasma[i].live){plasma_aim[i]=0;plasma[i].x=x;plasma[i].y=y;plasma_dx[i]=wave==7?0:(x<px?1:(x>px+16?-1:0));plasma[i].live=1;sfx_start(wave==7?FX_BOSS_FIRE:FX_ENEMY);break;}}
#include "waves.h"
#include "boss.h"
#include "player.h"
void render_fx(void){
 if(state==TRANSITION && explosion>2)explosion-=2;
 if(explosion){explosion--;pair(33,28+(explosion/6%3)*4,ex,ey);}else{hide_sprite(33);hide_sprite(34);}
}
void render(void){uint8_t i;
 for(i=0;i<10;i++){
 if(foes[i].live && foes[i].mode!=WAIT_ENTRY){
  if(!foes[i].kind){set_sprite_tile(13+i*2,48+((ticks>>3)&1)*2);move_sprite(13+i*2,foes[i].x+8,foes[i].y+16);hide_sprite(14+i*2);}
  else pair(13+i*2,4+foes[i].kind*8+((ticks>>3)&1)*4,foes[i].x,foes[i].y);
 }else{hide_sprite(13+i*2);hide_sprite(14+i*2);}}
 for(i=0;i<3;i++){set_sprite_tile(10+i,42);if(plasma[i].live)move_sprite(10+i,plasma[i].x+5,plasma[i].y+16);else hide_sprite(10+i);}
 render_fx();
}
void step(void){uint8_t i,j,alive=0;
 ticks++;
 if(fire_cd)fire_cd--;
 if(wave==7){
 boss_tick();
 if(++moon_clock==8){moon_clock=0;if(++moon_x>104)moon_x=8;}
 set_sprite_tile(35,64);move_sprite(35,moon_x+8,111);
 }else{
 waves_move();
 if(!fire_cd){
  fire_cd=fire_period;
  for(j=0;j<10;j++){if(++shooter>=10)shooter=0;if(foes[shooter].live && foes[shooter].mode!=WAIT_ENTRY && foes[shooter].y<120){fire_enemy(foes[shooter].x+(foes[shooter].kind?8:4),foes[shooter].y+(foes[shooter].kind?14:8));break;}}
 }
 for(i=0;i<10;i++)if(foes[i].live){Enemy *e=&foes[i];alive++;
 if(e->mode!=WAIT_ENTRY && e->live && hit(px+8,128,e->x-5,e->y-6,e->kind?26:18,e->kind?28:22)){
 if(shield_state==1){e->live=0;hide_enemy(i);add_score(10);boom(e->x,e->y);waves_reinforce(i);}else damage();}
 }
 if(!alive && state==PLAY){wave_clear_screen();return;}
 }
 for(i=0;i<3;i++)if(plasma[i].live){
 if((plasma_dx[i]<0 && plasma[i].x<2)||(plasma_dx[i]>0 && plasma[i].x>108)){plasma[i].live=0;continue;}
 if(plasma_aim[i]){plasma_error[i]+=(uint16_t)plasma_span[i]*plasma_speed;while(plasma_error[i]>=87){plasma_error[i]-=87;plasma[i].x+=plasma_dx[i];}}else plasma[i].x+=plasma_dx[i];plasma[i].y+=plasma_speed;if(plasma[i].y>143)plasma[i].live=0;
 else if(hit(plasma[i].x,plasma[i].y,px,120,16,16)){plasma[i].live=0;damage();}}
 render();
}
void main(void){
 DISPLAY_OFF;oam_init();BGP_REG=0x1b;OBP0_REG=0x1b;SPRITES_8x16;packed_tiles(sprite_data_rle,0,SPRITE_COUNT,1);packed_tiles(crow_data_rle,48,4,1);packed_tiles(ship_native_rle,52,12,1);set_sprite_data(64,2,moon_data);packed_tiles(ship_blast_data_rle,66,36,1);
 NR52_REG=0x80;NR50_REG=0x77;NR51_REG=0xff;record=0;add_VBL(timers);add_TIM(input_tick);TMA_REG=240;TIMA_REG=240;TAC_REG=0x04;set_interrupts(VBL_IFLAG|TIM_IFLAG);title();clock_last=sys_time;
 while(1){uint8_t elapsed,run_sim;
 /* If rendering crossed VBlank, consume that frame now instead of waiting twice. */
 if(sys_time==clock_last)wait_vbl_done();elapsed=(uint8_t)(sys_time-clock_last);clock_last=sys_time;
 CRITICAL {keys=joypad();pressed=input_press|(keys&~input_previous);input_previous=keys;input_now=keys;input_press=0;}if(shield_ready){shield_ready=0;sfx_start(FX_READY);}
 if(elapsed>4)elapsed=4;while(elapsed){sim_phase+=25;elapsed--;}run_sim=sim_phase>=60;if(run_sim)sim_phase-=60;
 if(sim_phase>120)sim_phase=0;
 if(state==TITLE){ticks++;if(pressed&(J_START|J_A)){new_game();}}
 else if(state==PLAY){if(pressed&J_START){paused=!paused;if(paused){audio_pause();text(4,9,"PAUSA",0);}else set_bkg_tiles(4,9,5,1,field+9*32+4);}if(!paused){player_tick();if(state==PLAY && run_sim)step();}}
 else if(state==MOAI_DEATH){if(run_sim && moai_death_tick())victory_screen();}
 else if(state==TRANSITION){
  if(pressed&J_START){paused=!paused;if(paused)audio_pause();}
  if(!paused){player_tick();if(run_sim)render_fx();if(state_timer)wave_clear_tick();else{wave++;spawn_wave();}}
 }
 else if(state==VICTORY){if(state_timer)state_timer--;else{if(phase<99)phase++;wave=1;px=48;invulnerable=120;setup_field();spawn_wave();}}
 else if(state==DYING){if(!death_timer){if(lives)respawn();else end_screen();}}
 else if(state==OVER){if(state_timer){state_timer--;if(!state_timer)text(4,16,"PRESS START",212);}else if(pressed&(J_START|J_A)){
 title();}}
 if(state==PLAY || state==DYING || state==TRANSITION)player_display();
 oam_commit();
 if(state==PLAY || state==DYING || state==TRANSITION){if(!paused){update_hud();hud_flush();if(state==PLAY && wave==7)moai_flush();}}
 }
}
