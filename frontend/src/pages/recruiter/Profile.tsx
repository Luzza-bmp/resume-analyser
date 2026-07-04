import { useState, useEffect, useRef, ChangeEvent, useCallback } from "react";
import axios from "axios";
import Cropper, { Area } from "react-easy-crop";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Camera, MapPin, Phone, Mail, User, Building, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function RecruiterProfile() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    location: "",
    company: "",
    role: "", // This is the job title in the UI
  });
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");
  const [croppedImage, setCroppedImage] = useState<string>("");
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [croppedBlob, setCroppedBlob] = useState<Blob | null>(null);
  const [avatarRemoved, setAvatarRemoved] = useState(false);
  const [previousImagePreview, setPreviousImagePreview] = useState<string>("");
  const [isCropping, setIsCropping] = useState(false);
  const [cameraMenuOpen, setCameraMenuOpen] = useState(false);
  const cameraMenuRef = useRef<HTMLDivElement | null>(null);
  const cameraButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
      setLoading(false);
      return;
    }

    const fetchProfile = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/api/profile/${userId}`);
        const fullName = response.data.name || "";
        const [firstName, ...lastNameParts] = fullName.split(" ");
        
        setProfile({
          firstName: firstName || "",
          lastName: lastNameParts.join(" ") || "",
          email: response.data.email || "",
          phone: response.data.phone || "",
          location: response.data.location || "",
          company: response.data.company || "",
          role: response.data.job_title || "",
        });
        if (response.data.avatar_url) {
          setImagePreview(response.data.avatar_url);
          setAvatarRemoved(false);
        } else {
          setImagePreview("");
          setAvatarRemoved(false);
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
        toast({
          title: "Error",
          description: "Failed to load profile data.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleSave = async () => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;

    setSaving(true);
    try {
      const formData = new FormData();
      formData.append("name", `${profile.firstName} ${profile.lastName}`.trim());
      formData.append("email", profile.email);
      formData.append("phone", profile.phone);
      formData.append("location", profile.location);
      formData.append("company", profile.company);
      formData.append("job_title", profile.role);

      if (avatarRemoved) {
        formData.append("remove_avatar", "true");
      } else if (croppedBlob) {
        formData.append("avatar", new File([croppedBlob], "avatar.jpg", { type: "image/jpeg" }));
      } else if (selectedFile) {
        formData.append("avatar", selectedFile);
      }

      const response = await axios.put(`http://127.0.0.1:5000/api/profile/${userId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      localStorage.setItem("user_name", `${profile.firstName} ${profile.lastName}`.trim());
      localStorage.setItem("user_job_title", profile.role || "");
      const savedAvatar = response.data.avatar_url || "";
      if (savedAvatar) {
        localStorage.setItem("avatar_url", savedAvatar);
      } else {
        localStorage.removeItem("avatar_url");
      }
      window.dispatchEvent(new Event("profile-changed"));

      toast({
        title: "Success",
        description: "Profile updated successfully.",
      });
    } catch (error) {
      console.error("Error saving profile:", error);
      toast({
        title: "Error",
        description: "Failed to save profile changes.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleImageChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setPreviousImagePreview(imagePreview);
    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);
    setSelectedFile(file);
    setIsCropping(true);
  };

  const handleUploadClick = () => {
    inputRef.current?.click();
  };

  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const createImage = (url: string): Promise<HTMLImageElement> =>
    new Promise((resolve, reject) => {
      const image = new Image();
      image.addEventListener("load", () => resolve(image));
      image.addEventListener("error", (error) => reject(error));
      image.setAttribute("crossOrigin", "anonymous");
      image.src = url;
    });

  const getCroppedImg = async (imageSrc: string, pixelCrop: Area) => {
    const image = await createImage(imageSrc);
    const canvas = document.createElement("canvas");
    canvas.width = pixelCrop.width;
    canvas.height = pixelCrop.height;
    const ctx = canvas.getContext("2d");

    if (!ctx) {
      throw new Error("Unable to get canvas context");
    }

    ctx.drawImage(
      image,
      pixelCrop.x,
      pixelCrop.y,
      pixelCrop.width,
      pixelCrop.height,
      0,
      0,
      pixelCrop.width,
      pixelCrop.height
    );

    return new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error("Canvas is empty"));
          return;
        }
        resolve(blob);
      }, "image/jpeg");
    });
  };

  const handleCropSave = async () => {
    if (!croppedAreaPixels || !imagePreview) return;
    try {
      const blob = await getCroppedImg(imagePreview, croppedAreaPixels);
      const croppedUrl = URL.createObjectURL(blob);
      setCroppedImage(croppedUrl);
      setImagePreview(croppedUrl);
      setCroppedBlob(blob);
      setIsCropping(false);
    } catch (error) {
      console.error("Crop error:", error);
      toast({
        title: "Error",
        description: "Unable to crop image.",
        variant: "destructive",
      });
    }
  };

  const handleCancelCrop = () => {
    setIsCropping(false);
    setSelectedFile(null);
    setImagePreview(previousImagePreview);
    setCroppedBlob(null);
    setPreviousImagePreview("");
    setZoom(1);
    setCrop({ x: 0, y: 0 });
  };

  const handleRemoveAvatar = () => {
    setSelectedFile(null);
    setCroppedBlob(null);
    setPreviousImagePreview("");
    setImagePreview("");
    setAvatarRemoved(true);
    setCameraMenuOpen(false);
  };

  const handleToggleCameraMenu = () => {
    setCameraMenuOpen((open) => !open);
  };

  const handleChangePicture = () => {
    setCameraMenuOpen(false);
    inputRef.current?.click();
  };

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      const target = event.target as Node;
      if (
        cameraMenuOpen &&
        cameraMenuRef.current &&
        cameraButtonRef.current &&
        !cameraMenuRef.current.contains(target) &&
        !cameraButtonRef.current.contains(target)
      ) {
        setCameraMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, [cameraMenuOpen]);

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#F97316]" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Recruiter Profile</h1>
        <p className="text-slate-500 mt-1">Manage your account and company details.</p>
      </div>

      <Card>
        <CardContent className="p-8">
          <div className="flex flex-col md:flex-row gap-8 items-start">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative group">
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageChange}
                />
                <button
                  type="button"
                  onClick={handleUploadClick}
                  className="p-0 bg-transparent border-0"
                >
                  <Avatar className="h-32 w-32 border-4 border-white shadow-md cursor-pointer">
                    {imagePreview ? (
                      <AvatarImage src={imagePreview} />
                    ) : (
                      <>
                        <AvatarImage src="" />
                        <AvatarFallback className="bg-[#F97316] text-white text-3xl font-bold">
                          {profile.firstName[0]}{profile.lastName[0]}
                        </AvatarFallback>
                      </>
                    )}
                  </Avatar>
                </button>
                <button
                  type="button"
                  ref={cameraButtonRef}
                  onClick={handleToggleCameraMenu}
                  className="absolute bottom-2 right-2 h-8 w-8 bg-[#F97316] text-white rounded-full flex items-center justify-center shadow-lg hover:bg-[#F97316]/90 transition-colors"
                >
                  <Camera className="h-4 w-4" />
                </button>
                {cameraMenuOpen ? (
                  <div
                    ref={cameraMenuRef}
                    className="absolute bottom-12 right-0 z-50 w-56 rounded-xl border border-slate-200 bg-white shadow-xl"
                  >
                    <button
                      type="button"
                      onClick={handleChangePicture}
                      className="w-full text-left px-4 py-3 hover:bg-slate-50"
                    >
                      Change profile picture
                    </button>
                    <button
                      type="button"
                      onClick={handleRemoveAvatar}
                      disabled={!imagePreview || avatarRemoved}
                      className="w-full text-left px-4 py-3 text-red-600 disabled:text-slate-400 hover:bg-slate-50 disabled:hover:bg-transparent"
                    >
                      Remove profile picture
                    </button>
                  </div>
                ) : null}
              </div>
              <p className="text-sm font-medium text-slate-500">JPG, GIF or PNG. Max size of 2MB.</p>
            </div>

            {isCropping && imagePreview ? (
              <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
                <div className="relative w-full max-w-2xl rounded-2xl bg-white p-4 shadow-xl">
                  <div className="relative h-[400px] w-full overflow-hidden rounded-2xl bg-slate-900">
                    <Cropper
                      image={imagePreview}
                      crop={crop}
                      zoom={zoom}
                      aspect={1}
                      onCropChange={setCrop}
                      onZoomChange={setZoom}
                      onCropComplete={onCropComplete}
                      cropShape="round"
                      showGrid={false}
                    />
                  </div>
                  <div className="mt-4 flex flex-col gap-4">
                    <div className="flex items-center gap-3">
                      <Label htmlFor="zoom">Zoom</Label>
                      <input
                        id="zoom"
                        type="range"
                        min={1}
                        max={3}
                        step={0.01}
                        value={zoom}
                        onChange={(e) => setZoom(Number(e.target.value))}
                        className="w-full"
                      />
                    </div>
                    <div className="flex justify-end gap-3">
                      <Button variant="outline" onClick={handleCancelCrop}>Cancel</Button>
                      <Button onClick={handleCropSave}>Save Crop</Button>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}

            <Separator orientation="vertical" className="hidden md:block h-auto" />

            <div className="flex-1 space-y-8 w-full">
              {/* Personal Details */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2 mb-4">Personal Details</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="firstName" 
                        value={profile.firstName} 
                        onChange={(e) => setProfile({ ...profile, firstName: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="lastName" 
                        value={profile.lastName} 
                        onChange={(e) => setProfile({ ...profile, lastName: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Work Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="email" 
                        type="email" 
                        value={profile.email} 
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="phone" 
                        type="tel" 
                        value={profile.phone} 
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Company Details */}
              <div className="space-y-6 pt-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2 mb-4">Company Details</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="company">Company Name</Label>
                    <div className="relative">
                      <Building className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="company" 
                        value={profile.company} 
                        onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="role">Your Role / Title</Label>
                    <Input 
                      id="role" 
                      value={profile.role} 
                      onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="location">Office Location</Label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input 
                        id="location" 
                        value={profile.location} 
                        onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                        className="pl-9" 
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-4 pt-6 mt-6 border-t border-slate-100">
                <Button variant="outline">Cancel</Button>
                <Button 
                  className="bg-[#1E3A5F] hover:bg-[#1E3A5F]/90"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    "Save Profile"
                  )}
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
