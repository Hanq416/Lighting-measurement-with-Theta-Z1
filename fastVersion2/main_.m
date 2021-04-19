clear all; %#ok<*CLALL>
close all;
clc;
% illuminance map with 360 Pano-Camera (Ricoh Theta Z1)
% Type source file: [dual fisheye hdr image]
% Hankun Li, University of Kansas 
% Lighting Research Laboratory 
% update: 02/09/2021, version 1.4, H.Li contrast map function added
%
%Author Notes:
%[1]illuminance map is to show the distribution of percieved light.
%user need to evaluate based on the whole map, check gradient.
%[2]CV_map is to show light uniformity at every specified direction, high
%number means at specific direction, light in 180-deg view is not uniform

%% Camera parameters (Ricoh Theta Z1):
%--------- Camera parameters -----------%
%DO NOT CHANGE FOR THETA Z1 CAMERA!
f = 3; % specify lens focal length ##(INPUT2)##
% sx = sy = f*1.414*2
sx = 8.48; sy = 8.48; % Calculated sensor size (Single 180deg fisheye)
%---------Camera parameters end---------%

%% UI initialization:
cd ./lib_360;
%% pre-processing, pre-calculation
[fn,pn]=uigetfile('*.hdr','select a dual fisheye 360 hdr image');str=[pn,fn];
[tilt_a,tilt_b,aim_a,aim_b,aim_step,gcf,comr] = initial_dialog();
I = hdrread(str); vmsk = vecorf; I = I./vmsk;
exp = getExpValue(str); gcf = gcf./exp;
fprintf('\n Notes: Re-calculation of GCF for old data, exp is now counted! \n');
pano = imgstiching_hdr(I); [y1,x1] = size(pano(:,:,1));
pano = imresize(pano,[round(y1/comr),round(x1/comr)]);
[y,x] = size(pano(:,:,1)); tilt_step = aim_step;
clear pn fn str;
% hdrGammaShow(I, 0.5); % show HDR image.
%% create a queue:
i = aim_a; illu_map = []; ct = 1;
while i <= aim_b
    j = tilt_a; %ta
    while j <= tilt_b
        illu_map(ct,1) = j; illu_map(ct,2) = i + 180; % tmp, principle angle correction (0 or 180)
        ct = ct + 1;
        j  = j + tilt_step;
    end
    i = i + aim_step; %aa
end

%% angle-based illuminance calibration (optional, click No to skip)
icf_flg = 0;
yn = yn_dialog('Apply angel based illuminance calibration?');
if ismember(yn, ['Yes', 'yes'])
    tf = tf_dialog('Reference lux point? [2 or 5]'); %see reference or papaer to understand 2-ref/5-ref methods.
    if ismember(tf, ['2-ref','2-REF'])
        [cfh,cfv0,cfv90,cfv180,cfv270] = getluxCF_2ref(pano,gcf,sx,sy,f);
    else
        [cfh,cfv0,cfv90,cfv180,cfv270] = getluxCF(pano,gcf,sx,sy,f);
    end
    fprintf('\nIlluminance calibration factor: \n');
    fprintf('Eh:%f, E@0:%f, E@90:%f, E@180:%f, E@-90:%f\n', cfh,cfv0,cfv90,cfv180,cfv270);
    icf_flg = 1;
end
%make sure understand 5 reference values first before click 'yes' to use
%icf function end

%% Generate a CV (coefficient of variance) map?
cv_flg = 0;
yn = yn_dialog('Generate Coefficient of Variance Map?');
if ismember(yn, ['Yes', 'yes'])
    cv_flg = 1;
end

%% Generate a CR (contrast ratio) map?
cr_flg = 0; default_y = 800;
yn = yn_dialog('Generate Contrast Ratio Map?');
if ismember(yn, ['Yes', 'yes'])
    cr_flg = 1;
    [msk2,msk4,msk10,msk30,msk90] = genMask(f, sy, default_y);
end
%% create anuglar factor mask
refHDR = imequ2fish_hdr(pano,0,0,90);
[yc,xc] = size(refHDR(:,:,1));
luxmask = equisolidMask(xc,yc,180);
clear xc yc;
%% main function
for z = 1: size(illu_map,1)
    IF_hdr = imequ2fish_hdr(pano,illu_map(z,1),illu_map(z,2),90);
    [hy, hx] = size(IF_hdr(:,:,1));
    if hy ~= hx
        IF_hdr = imresize(IF_hdr, [hy,hy]);
        luxmask = imresize(luxmask, [hy,hy]);
    end
    L = LuminanceRetrieve(IF_hdr.*gcf,hy);%temporary global CF function!
    if icf_flg %illuminance map with angle-based calibration
        raw_lux = FASTequisolid(IF_hdr,luxmask,gcf);
        illu_map(z,3) = luxCalib(raw_lux,illu_map(z,2),illu_map(z,1),cfh,cfv0,cfv90,cfv180,cfv270);
    else
        illu_map(z,3) = FASTequisolid(IF_hdr,luxmask,gcf);%#ok<*SAGROW>
    end
    if cv_flg
        illu_map(z,4) = std(L(:,3))/mean(L(:,3)); %CV map, gen source data
    end
    if cr_flg
        [illu_map(z,5),illu_map(z,6),illu_map(z,7),illu_map(z,8)] = getContrast(IF_hdr, gcf,...
            hy, msk2, msk4, msk10, msk30, msk90); %CR map, gen source data
    end
end
clear msk2 msk4 msk10 msk30 msk90; 

%% illuminance plot
illuminancePlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
    'illuminance Map',1) %plot illuminance map

%% CV plot
if cv_flg
    CVPlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
        'Coefficient of Variation Map',2) %plot cv map
end

%% CR plot
% parameters notes: first line--- no need of changes
% second line: figure Name, source data code, gamma correction
if cr_flg
    CRPlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
        'Near-background luminance contrast Map',5,1);
    CRPlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
        'Far-background luminance contrast Map',6,1);
    CRPlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
        'Near-background luminance ratio Map',7,0.8);
    CRPlot(illu_map,tilt_step,aim_step,tilt_a,tilt_b,aim_a,aim_b,...
        'Far-background luminance ratio Map',8,0.8);
end

%% Generate statistic report
yn = yn_dialog('Generate a simple report?');
if ismember(yn, ['Yes', 'yes'])
    staReport(illu_map,cv_flg,cr_flg);
end

%% Generate stichited panoramic luminance map?
yn = yn_dialog('Generate panoramic luminance map?');
if ismember(yn, ['Yes', 'yes'])
    Luminance_map(pano,'Luminance map',10, 0.25, gcf); % source hdri, name, code, gamma value
end
%% reset dir
cd ../;

%% Generate Evaluation function [unquote to use!]
% Must have reference data first. For fast HDRi accurac check.

eval_map = illu_map; 
eval_map(:,2) = eval_map(:,2); % [+- 180*]
eval_map(:,5:8) = []; % [*]
% evaluation fucntion: Evalsim(eval_map);

% end here!
% save eval_map as a mat file as reference data for rhino evaluation
%%
Luminance_map(IF_hdr,'Luminance map',3, 0.25, gcf);