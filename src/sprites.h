/* The SDK shadow is the working frame. DMA reads one of two completed pages.
   Committing a page flips one byte; no interrupt is blocked during drawing. */
uint8_t oam_pages[672],oam_flip;
uint8_t *oam_frame[2];
void oam_init(void){uint16_t aligned=((uint16_t)oam_pages+255)&0xff00;
 oam_frame[0]=(uint8_t *)aligned;oam_frame[1]=(uint8_t *)(aligned+256);
 memset(oam_frame[0],0,160);memset(oam_frame[1],0,160);oam_flip=0;
 _shadow_OAM_base=aligned>>8;
}
void oam_commit(void){oam_flip^=1;memcpy(oam_frame[oam_flip],(const void *)shadow_OAM,160);_shadow_OAM_base=(uint16_t)oam_frame[oam_flip]>>8;}
