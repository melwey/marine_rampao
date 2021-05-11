# plot Results of PA coverage of marine habitats
setwd("E:/weyname/BIOPAMA/GIS/Marine/RAMPAO")

# run pyCode: map_by_country_rampao.py

library(readr)
library(ggplot2)
library(dplyr)
library(stringr)
library(FAOSTAT)
layers <- c("coral", "seagrass", "mangrove", "modSeagrass")
rampao <- c('CPV', 'GIN', 'GMB', 'GNB', 'MRT', 'SEN', 'SLE')
alldata <- NULL
for (layer in layers) {
  data <- read_csv(paste0("./output/tables/", layer, "_RAMPAO.csv"),
                   na='NULL',
                   col_types = cols(iso3 = col_factor(rampao),
                                    iso3_pa = col_factor(rampao),
                                    pa = col_factor()
                                    )
                   )
  if (nrow(data) < 1){next}
  data$layer <- factor(layer, levels = layers)
  alldata <- rbind(alldata, data)
}

alldata$layer <- factor(alldata$layer, levels = layers)
alldata$pa <- factor(alldata$pa)
# add zero data to missing levels
alldata <- alldata %>%
  tidyr::complete(iso3, layer, pa) %>%
  tidyr::replace_na(list(AreaSqkm = 0))
alldata <- alldata %>% left_join(FAOcountryProfile %>% select(ISO3_CODE, SHORT_NAME), by = c("iso3" = "ISO3_CODE"))
  
eco_cols = c('coral' = '#e65025', 'seagrass' = '#36aa49', 'mangrove' = '#720f11', 'modSeagrass' = '#36aa49')
col_pa <- c("0" = "#ffffff", "1" = "#70b6d1")
coralGrob <- grid::rasterGrob(png::readPNG("../img/coral_logo.png"), interpolate=TRUE)
seagrassGrob <- grid::rasterGrob(png::readPNG("../img/seagrass_logo.png"), interpolate=TRUE)
mangroveGrob <- grid::rasterGrob(png::readPNG("../img/mangroves_logo.png"), interpolate=TRUE)

# p <- ggplot(data = alldata %>% filter(layer != "modSeagrass" & layer != "coral"),
#             aes(x = SHORT_NAME, y = AreaSqkm, fill = layer, colour = pa)
#             ) + 
#   geom_bar(stat = 'identity', position='dodge') +
#   scale_fill_manual(values = eco_cols) +
#   scale_colour_manual(values = col_pa, labels = c("0" = "Not protected", "1" = "Protected")) +
#   scale_x_discrete(labels = function(x) str_wrap(x, width = 11)) +
#   xlab("") +
#   ylab("Area [sq. km]") +
#   guides(fill = "none", colour = guide_legend("Protection")) +
#   facet_grid(layer~., scale = 'free') +
#   theme(plot.background = element_blank())
# 
# base <- ggplot(data.frame(x=1:10, y=1:10), aes(x,y)) +
#   geom_blank() +
#   theme_void() +
#   # annotation_custom(grob = coralGrob, xmin = 8.5, xmax = 10, ymin = 7.125, ymax = 8.625) +
#   annotation_custom(grob = seagrassGrob, xmin = 8.5, xmax = 10, ymin = 6.375, ymax = 8.875) +
#   annotation_custom(grob = mangroveGrob, xmin = 8.5, xmax = 10, ymin = 2.375, ymax = 3.875) +
#   coord_fixed(ratio = 1/1)
# p1 <- base + 
#   annotation_custom(grob = ggplotGrob(p), xmin=1, xmax = 10, ymin = 0, ymax = 10)+ 
#   labs(title = "Marine Key Biodiversity Habitats Distribution in RAMPAO countries")
# ggsave("marine_distribution_protection.png", width=12, height = 12, units = "cm")
# 
# # position='fill'
# p <- ggplot(data = alldata %>% filter(layer != "modSeagrass" & layer != "coral"),
#             aes(x = SHORT_NAME, y = AreaSqkm, fill = pa)
# ) + 
#   geom_bar(stat = 'identity', position='fill', size=1) +
#   scale_fill_manual(values = col_pa, labels = c("0" = "Not protected", "1" = "Protected")) +
#   scale_x_discrete(labels = function(x) str_wrap(x, width = 11)) +
#   xlab("") +
#   ylab("Area [sq. km]") +
#   guides(fill = guide_legend("Protection")) +
#   facet_grid(layer~., scale = 'free') +
#   theme(plot.background = element_blank())
# p1 <- base + 
#   annotation_custom(grob = ggplotGrob(p), xmin=1, xmax = 10, ymin = 0, ymax = 10)+ 
#   labs(title = "Marine Key Biodiversity Habitats Distribution in RAMPAO countries")
# ggsave("marine_distribution_protection_pc.png", width=12, height = 12, units = "cm")
# 
# 
# p <- ggplot(data = alldata %>% filter(layer == "modSeagrass"), 
#             aes(x = SHORT_NAME, y = AreaSqkm, fill = layer, colour = pa)) +
#   geom_bar(stat = 'identity', position='dodge') +
#   scale_fill_manual(values = eco_cols) +
#   scale_colour_manual(values = col_pa, labels = c("0" = "Not protected", "1" = "Protected")) +
#   scale_x_discrete(labels = function(x) str_wrap(x, width = 11)) +
#   guides(fill = "none", colour = guide_legend("Protection")) +
#   labs(title = "Modelled seagrass suitability in RAMPAO countries") +
#   xlab("") +
#   ylab("Area [sq. km]")
# p
# ggsave("segrass_suitability.png",p, width = 12, height = 5, units = "cm")
# 
# # 
# p <- ggplot(data = alldata %>% filter(layer == "modSeagrass"), 
#             aes(x = SHORT_NAME, y = AreaSqkm, fill = pa)) +
#   geom_bar(stat = 'identity', position='fill') +
#   scale_fill_manual(values = col_pa, labels = c("0" = "Not protected", "1" = "Protected")) +
#   scale_x_discrete(labels = function(x) str_wrap(x, width = 11)) +
#   guides(fill = guide_legend("Protection")) +
#   labs(title = "Modelled seagrass suitability in RAMPAO countries") +
#   xlab("") +
#   ylab("Area [sq. km]")
# ggsave("segrass_suitability_pc.png",p, width = 12, height = 5, units = "cm")

##rearrange alldata
allData <- alldata %>% 
  # total area
  left_join(alldata %>% group_by(iso3, layer) %>% summarise(AreaTotSqkm = sum(AreaSqkm))) %>% 
  # # keep only entries with protection or disputed waters
  # filter(pa == 1 | nchar(as.character(iso3)) > 3 & AreaTotSqkm > 0) %>%
  mutate(AreaProtSqkm = AreaSqkm * as.numeric(as.character(pa))) %>%
  # drop areas protected by another country and disputed waters
  mutate(pa = as.logical(as.numeric(as.character(pa)))) %>%
  filter((pa & iso3 == iso3_pa) | (!pa & nchar(iso3)==3)) %>%
  select(-AreaSqkm, -iso3_pa) %>%
  tidyr::spread(key = pa, value = AreaProtSqkm, fill = 0) %>%
  select(-`FALSE`) %>%
  rename(AreaProtSqkm = `TRUE`) %>%
  mutate(AreaUnprotSqkm = AreaTotSqkm - AreaProtSqkm) %>%
  mutate(AreaProtPC = round(AreaProtSqkm/AreaTotSqkm*100)) %>%
  # sort by layer
  arrange(layer)
write_csv(allData, "RAMPAO_marine_habitat_protection_data_wdpaJul2018.csv")

# coral
p <- ggplot(data = filter(allData, layer == 'coral') %>%
              tidyr::gather(AreaProtSqkm, AreaUnprotSqkm, key = "protection", value = "Area") %>%
              mutate(protection = ifelse(protection =='AreaProtSqkm', 'protected', 'not protected')) %>%
              mutate(AreaTot = ifelse(protection == 'not protected', NA, AreaTotSqkm)) %>%
              mutate(pc = round(Area/AreaTotSqkm*100)) %>%
              tidyr::replace_na(list(pc = 0)),
            aes(x = SHORT_NAME, y = Area, fill = protection)) +
  geom_bar(stat = 'identity') + 
  scale_fill_manual(values = c('#e6502555','#e65025')) +
  geom_label(aes(label = paste0(round(pc), '%'), y = AreaTot), nudge_y = 150, show.legend = FALSE) +
  labs(title = "Distribution and protection of warm water corals",
       x = "Country",
       y = bquote(Area~(km^{2})),
       fill = "Protected") +
  theme(
    panel.border = element_rect(fill=NA, colour = "black"),
    plot.background = element_rect(fill = "transparent"),
    panel.background = element_rect(fill = "transparent"),
    panel.grid.major.y = element_line(colour = "black"),
    panel.grid.minor.y = element_line(colour = "gray40")
  )
p
ggsave("coral_distribution_RAMPAO.png",p, width = 27, height = 16, units = "cm")

# mangrove
p <- ggplot(data = filter(allData, layer == 'mangrove') %>%
              tidyr::gather(AreaProtSqkm, AreaUnprotSqkm, key = "protection", value = "Area") %>%
              mutate(protection = ifelse(protection =='AreaProtSqkm', 'protected', 'not protected')) %>%
              mutate(AreaTot = ifelse(protection == 'not protected', NA, AreaTotSqkm)) %>%
              mutate(pc = round(Area/AreaTotSqkm*100)) %>%
              tidyr::replace_na(list(pc = 0)),
            aes(x = SHORT_NAME, y = Area, fill = protection)) +
  geom_bar(stat = 'identity') + 
  scale_fill_manual(values = c('#720f1155','#720f11')) +
  geom_label(aes(label = paste0(round(pc), '%'), y = AreaTot), nudge_y = 150, show.legend = FALSE, colour = "#ffffff") +
  labs(title = "Distribution and protection of mangroves",
       x = "Country",
       y = bquote(Area~(km^{2})),
       fill = "Protected") +
  theme(
    panel.border = element_rect(fill=NA, colour = "black"),
    plot.background = element_rect(fill = "transparent"),
    panel.background = element_rect(fill = "transparent"),
    panel.grid.major.y = element_line(colour = "black"),
    panel.grid.minor.y = element_line(colour = "gray40")
  )
p
ggsave("mangrove_distribution_RAMPAO.png",p, width = 27, height = 16, units = "cm")

p <- ggplot(data = filter(allData, layer == 'seagrass') %>%
              tidyr::gather(AreaProtSqkm, AreaUnprotSqkm, key = "protection", value = "Area") %>%
              mutate(protection = ifelse(protection =='AreaProtSqkm', 'protected', 'not protected')) %>%
              mutate(AreaTot = ifelse(protection == 'not protected', NA, AreaTotSqkm)) %>%
              mutate(pc = round(Area/AreaTotSqkm*100)) %>%
              tidyr::replace_na(list(pc = 0)),
            aes(x = SHORT_NAME, y = Area, fill = protection)) +
  geom_bar(stat = 'identity') + 
  scale_fill_manual(values = c('#b2df8a','#36aa49')) +
  geom_label(aes(label = paste0(round(pc), '%'), y = AreaTot), nudge_y = 150, show.legend = FALSE) +
  labs(title = "Distribution and protection of seagrass beds",
       x = "Country",
       y = bquote(Area~(km^{2})),
       fill = "Protected") +
  theme(
    panel.border = element_rect(fill=NA, colour = "black"),
    plot.background = element_rect(fill = "transparent"),
    panel.background = element_rect(fill = "transparent"),
    panel.grid.major.y = element_line(colour = "black"),
    panel.grid.minor.y = element_line(colour = "gray40")
  )
p
ggsave("seagrass_distribution_RAMPAO.png",p, width = 27, height = 16, units = "cm")

p <- ggplot(data = filter(allData, layer == 'modSeagrass') %>%
              tidyr::gather(AreaProtSqkm, AreaUnprotSqkm, key = "protection", value = "Area") %>%
              mutate(protection = ifelse(protection =='AreaProtSqkm', 'protected', 'not protected')) %>%
              mutate(AreaTot = ifelse(protection == 'not protected', NA, AreaTotSqkm)) %>%
              mutate(pc = round(Area/AreaTotSqkm*100)) %>%
              tidyr::replace_na(list(pc = 0)),
            aes(x = SHORT_NAME, y = Area, fill = protection)) +
  geom_bar(stat = 'identity') + 
  scale_fill_manual(values = c('#b2df8a','#36aa49')) +
  geom_label(aes(label = paste0(round(pc), '%'), y = AreaTot), nudge_y = 1000, show.legend = FALSE) +
  labs(title = "Distribution and protection of habitat suitable for seagrass (modelled)",
       x = "Country",
       y = bquote(Area~(km^{2})),
       fill = "") +
  theme(
    panel.border = element_rect(fill=NA, colour = "black"),
    plot.background = element_rect(fill = "transparent"),
    panel.background = element_rect(fill = "transparent"),
    panel.grid.major.y = element_line(colour = "black"),
    panel.grid.minor.y = element_line(colour = "gray40")
  )
p
ggsave("modSeagrass_distribution_RAMPAO.png",p, width = 27, height = 16, units = "cm")


# compare with lucy's data
data <- read_csv(paste0("./seagrass_RAMPAO.csv"), na='NULL')
data %>% left_join(data %>% group_by(iso3) %>% summarise(AreaTot = sum(AreaSqkm))) %>% filter(!is.na(iso3_pa)) %>%select(-pa) %>% mutate(AreaProtPc = AreaSqkm/AreaTot*100)
dataLucy <- read_csv(paste0("../lucy_rampao_results/seagrass_protection.csv"))
seagrassLucy <- dataLucy %>% mutate(seagrass_prot_pc = seagrass_prot_km/seagrass_km*100)

data %>%
  left_join(data %>%
              group_by(iso3) %>%
              summarise(AreaTot = sum(AreaSqkm))) %>%
  filter(!is.na(iso3_pa)) %>%
  select(-pa) %>% mutate(AreaProtPc = AreaSqkm/AreaTot*100) %>%
  left_join(seagrassLucy, by=c('iso3'='iso3', 'iso3_pa'= 'country_protecting_seagrass'), suffix=c(".mel",".lucy"))
# percentages are equal, but Lucy's absolute values are twice as big as mine?!?

data <- read_csv(paste0("../mangrove_RAMPAO.csv"), na='NULL')
data %>% left_join(data %>% group_by(iso3) %>% summarise(AreaTot = sum(AreaSqkm))) %>% filter(!is.na(iso3_pa)) %>%select(-pa) %>% mutate(AreaProtPc = AreaSqkm/AreaTot*100)
dataLucy <- read_csv(paste0("../lucy_rampao_results/mangrove_protection.csv"))
mangroveLucy <- dataLucy %>% mutate(mangrove_prot_pc = mangrove_prot_km/mangrove_km*100)
# areas and percenrages are in the same range, but not equal

