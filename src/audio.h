/* Nonblocking DMG soundtrack: dark techno + short native pulse/noise effects.
   Pulse 1 = effects; pulse 2 + wave = music; noise is shared with FX priority. */
#define FX_SHOT 1
#define FX_ENEMY 2
#define FX_BOSS_FIRE 3
#define FX_EXPLODE 4
#define FX_HIT 5
#define FX_SHIELD 6
#define FX_READY 7
#define FX_LIFE 8
#define FX_DEATH 9
#define FX_COLLAPSE 10
volatile uint8_t music_on,fx_id,fx_index,fx_wait,fire_voice;
uint8_t music_clock,music_step,title_light,noise_hold,bass_drop;
uint16_t bass_pitch;
volatile uint8_t music_song,music_pending;
uint8_t over_clock,over_note;
const uint8_t fx_lengths[]={0,1,2,2,3,2,3,2,4,4,5};
const uint8_t fx_priority[]={0,1,1,2,2,2,3,2,4,5,5};
/* D minor with a flattened second: a restrained, darker four-bar pattern. */
const uint16_t techno_bass[4]={1155,1155,1297,1205};
const uint16_t techno_notes[8]={1825,1899,1860,1837,1825,1915,1899,1860};
const uint16_t over_notes[5]={1825,1750,1673,1601,1155};
const uint8_t over_lengths[5]={10,10,14,18,44};
const uint16_t shield_notes[3]={1750,1825,1899};
const uint16_t life_notes[4]={1825,1860,1899,1936};
void audio_pulse(uint16_t f,uint8_t vol,uint8_t length){NR10_REG=0;NR11_REG=0x40|length;NR12_REG=vol;NR13_REG=f;NR14_REG=0xc0|(f>>8);}
void audio_noise(uint8_t pitch,uint8_t vol,uint8_t length){NR41_REG=length;NR42_REG=vol;NR43_REG=pitch;NR44_REG=0xc0;}
void sfx_start(uint8_t id){CRITICAL {if(!fx_id||fx_priority[id]>=fx_priority[fx_id]){fx_id=id;fx_index=0;fx_wait=0;}}}
/* 0.18: CAÑON DE PLASMA ESF-01. Dos etapas en canal de ruido 4.
   Descarga inicial + soplido más grave al siguiente VBlank.
   Ninguna nota ni oscilador tonal en el disparo. */
void audio_fire_now(void){CRITICAL {
 NR12_REG=0x00; /* silenciar canal tonal anterior */
 NR41_REG=0x39;NR42_REG=0xf1;NR43_REG=0x15;NR44_REG=0xc0;
 noise_hold=0x83;fire_voice=2;
}}
void audio_stop_music(void){music_on=0;NR12_REG=0;NR22_REG=0;NR30_REG=0;NR42_REG=0;fx_id=0;fire_voice=0;noise_hold=0;BGP_REG=0x1b;NR50_REG=0x77;}
void audio_over(void){audio_stop_music();over_note=0;over_clock=1;}
void audio_wave(void){music_pending=0;music_song=0;}
void audio_title(void){uint8_t i;const uint8_t bass_wave[16]={0x01,0x24,0x68,0xac,0xef,0xff,0xed,0xcb,0xa9,0x87,0x65,0x43,0x21,0x10,0x00,0x00};
 audio_stop_music();NR30_REG=0;for(i=0;i<16;i++)((volatile uint8_t *)0xff30)[i]=bass_wave[i];
 music_clock=0;music_step=0;music_song=0;music_pending=0;over_clock=0;title_light=0;bass_drop=0;music_on=1;
}
void audio_game(void){CRITICAL {music_song=0;music_pending=0;over_clock=0;BGP_REG=0x1b;music_clock=0;music_step=0;bass_drop=0;fx_id=0;fire_voice=0;noise_hold=0;NR12_REG=0;NR22_REG=0;NR42_REG=0;music_on=1;}}
void audio_pause(void){NR12_REG=0;NR22_REG=0;NR32_REG=0;NR42_REG=0;fx_id=0;fire_voice=0;noise_hold=0;}
/* Title only: original 90s Eurodance hook; exact equal-tempered Am/F/C/G, ~132 BPM. */
const uint16_t trance_arp[16]={1452,1547,1650,1547,1297,1452,1547,1452,1547,1650,1714,1650,1379,1517,1602,1517};
const uint16_t trance_lead[32]={1650,1750,1798,1750,1750,1798,1750,1673,1714,1650,1714,1798,1783,1750,1714,1602,1650,1750,1798,1849,1798,1750,1714,1673,1650,1714,1798,1714,1602,1714,1783,1714};
const uint16_t trance_bass[4]={1452,1297,1547,1379};
void audio_trance_tick(void){uint8_t k,chord;uint16_t f;
 title_light++;if(title_light==24||title_light==96)BGP_REG=0x0b;if(title_light==32||title_light==104)BGP_REG=0x1b;
 music_clock+=22;if(music_clock<149)return;music_clock-=149;
 k=music_step&15;chord=(music_step>>4)&3;
 if(k&1){f=trance_arp[chord*4+((music_step>>1)&3)];NR21_REG=0xa8;NR22_REG=0x22;NR23_REG=f;NR24_REG=0xc0|(f>>8);}
 if(!(music_step&3)){audio_pulse(trance_lead[music_step>>2],0x53,8);NR11_REG=0x88;}
 if((k&3)==2){f=trance_bass[chord];NR30_REG=0x80;NR31_REG=192;NR32_REG=0x40;NR33_REG=f;NR34_REG=0xc0|(f>>8);}
 if(!(k&3))audio_noise(k==4||k==12?0x15:0x54,0x51,57);
 else if(k&1)audio_noise(0x03,0x21,63);
 music_step=(music_step+1)&127;
}
void audio_tick(void){uint16_t f;uint8_t k,duck;
 if(paused)return;
 if(state==OVER){
  if(over_clock && !--over_clock && over_note<5){
   audio_pulse(over_notes[over_note],0x64,over_note==4?0:40);over_clock=over_lengths[over_note++];
  }return;
 }
 if(state==TITLE && music_on){audio_trance_tick();return;}
 if(fire_voice)fire_voice--;
 if(noise_hold==0x83){
   /* Fase 2: cola de plasma más suave y grave. */
   NR41_REG=0x39;NR42_REG=0x61;NR43_REG=0x45;NR44_REG=0xc0;
   noise_hold=3;
  }else if(noise_hold)noise_hold--;
 duck=fx_id>=FX_EXPLODE;
 if(music_on){
  NR32_REG=state==DYING?0:0x60;
  if(bass_drop && !--bass_drop){NR33_REG=bass_pitch;NR34_REG=0x40|(bass_pitch>>8);}
  music_clock+=22; /* 132 BPM approximately, independent of rendering. */
  if(music_clock>=149){music_clock-=149;k=music_step&15;if(!k)music_song=0;
   if(0x4449u&(1u<<k)){
    f=techno_notes[(music_step>>3)&7];NR21_REG=0x70;NR22_REG=duck?0x12:0x32;NR23_REG=f;NR24_REG=0xc0|(f>>8);
   }
   if(0x494du&(1u<<k)){
    bass_pitch=techno_bass[(music_step>>4)&3];f=bass_pitch;
    if(!(k&3)){f=2048-((2048-f)>>1);bass_drop=2;}
    NR30_REG=0x80;NR31_REG=210;NR33_REG=f;NR34_REG=0xc0|(f>>8);
   }
   if(!noise_hold && !duck){
    if(!(k&3))audio_noise((k==4||k==12)?0x15:0x54,(k==4||k==12)?0x42:0x51,57);
    else if(k&1)audio_noise(0x03,0x21,63);
   }
   music_step=(music_step+1)&63;
  }
 }
 if(!fx_id)return;
 if(fx_wait){fx_wait--;return;}
 /* El disparo de plasma es inmediato; otros efectos tonales esperan su ataque. */
 if(fire_voice && (fx_id<=3||fx_id==FX_SHIELD||fx_id==FX_READY||fx_id==FX_LIFE))return;
 k=fx_index++;
 switch(fx_id){
 case FX_SHOT:audio_fire_now();break;
 case FX_ENEMY:audio_pulse(k?1783:1849,0x52,60);break;
 case FX_BOSS_FIRE:audio_pulse(k?1714:1783,0x72,56);break;
 case FX_EXPLODE:audio_noise(0x24+(k<<4),0x92,52);noise_hold=5;break;
 case FX_HIT:audio_noise(k?0x25:0x14,0x72,60);noise_hold=3;break;
 case FX_SHIELD:audio_pulse(shield_notes[k],0x63,50);break;
 case FX_READY:audio_pulse(k?1936:1899,0x62,54);break;
 case FX_LIFE:audio_pulse(life_notes[k],0x73,48);break;
 case FX_DEATH:audio_noise(0x35+(k<<4),0xb2,46);noise_hold=6;break;
 case FX_COLLAPSE:audio_noise(0x45+((k&1)<<4),0xa2,48);noise_hold=6;break;
 }
 fx_wait=(fx_id==FX_LIFE||fx_id==FX_SHIELD)?4:2;
 if(fx_index>=fx_lengths[fx_id])fx_id=0;
}
