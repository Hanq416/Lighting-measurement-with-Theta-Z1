%Retriving Luminance Map
function lumi = LuminanceRetrieve(I,y)
R = I(:,:,1); G = I(:,:,2); B = I(:,:,3); lumi = [];
Lraw = (R.*0.2126 + G.*0.7152 + B.*0.0722).*179; %Inanici, D65-white
[lumi(:,2),lumi(:,1)]=find(Lraw);
for i = 1:size(lumi,1)
    lumi(i,3) = Lraw(lumi(i,2),lumi(i,1));
end
lumi(:,2) = y - lumi(:,2);
end