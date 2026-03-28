"use client";

import { type ReactNode, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { type FacultyProfileData, type ReviewRequestData, type ReviewStatus } from "@/lib/api-client";
import {
  useAcceptReview,
  useCompleteReview,
  useDeclineReview,
  useFacultyList,
  useIncomingReviews,
  useRequestReview,
} from "@/hooks/use-collaboration";
import { useProjectsList } from "@/hooks/use-projects";
import { useAuthStore } from "@/stores/auth-store";
import {
  Users,
  UserCheck,
  Clock,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Send,
} from "lucide-react";

const STATUS_COLORS: Record<ReviewStatus, string> = {
  pending: "bg-amber-100 text-amber-800",
  accepted: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  declined: "bg-red-100 text-red-800",
};

const STATUS_ICONS: Record<ReviewStatus, ReactNode> = {
  pending: <Clock className="h-4 w-4" />,
  accepted: <UserCheck className="h-4 w-4" />,
  completed: <CheckCircle2 className="h-4 w-4" />,
  declined: <XCircle className="h-4 w-4" />,
};

function FacultyCard({
  faculty,
  onRequestReview,
  isStudent,
  canRequest,
  isSubmitting,
}: {
  faculty: FacultyProfileData;
  onRequestReview: (facultyId: string) => void;
  isStudent: boolean;
  canRequest: boolean;
  isSubmitting: boolean;
}) {
  const t = useTranslations("collaborate");
  const areas = faculty.expertise_areas?.areas || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="text-base">{t("department")}: {faculty.department}</CardTitle>
            <CardDescription className="mt-1">
              {areas.length > 0 ? (
                <span className="flex flex-wrap gap-1">
                  {areas.map((area) => (
                    <Badge key={area} variant="secondary" className="text-xs">
                      {area}
                    </Badge>
                  ))}
                </span>
              ) : (
                "-"
              )}
            </CardDescription>
          </div>
          {faculty.available_for_review ? (
            <Badge className="bg-green-100 text-green-800">{t("availableForReview")}</Badge>
          ) : (
            <Badge variant="outline">{t("unavailable")}</Badge>
          )}
        </div>
      </CardHeader>
      {isStudent && faculty.available_for_review && (
        <CardContent>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={!canRequest || isSubmitting}
            onClick={() => onRequestReview(faculty.id)}
          >
            <MessageSquare className="mr-1 h-4 w-4" />
            {t("requestReview")}
          </Button>
        </CardContent>
      )}
    </Card>
  );
}

function ReviewCard({
  review,
  onAccept,
  onDecline,
  onComplete,
  busy,
}: {
  review: ReviewRequestData;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
  onComplete: (id: string, text: string) => void;
  busy: boolean;
}) {
  const t = useTranslations("collaborate");
  const [reviewText, setReviewText] = useState("");
  const [showForm, setShowForm] = useState(false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-sm font-medium">{t("reviewStatus")}</CardTitle>
            <CardDescription className="text-xs">
              {new Date(review.created_at).toLocaleDateString()}
            </CardDescription>
          </div>
          <Badge className={`flex items-center gap-1 ${STATUS_COLORS[review.status]}`}>
            {STATUS_ICONS[review.status]}
            {t(review.status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {review.review_text && (
          <div className="mb-3 rounded-lg bg-(--muted) p-3">
            <p className="text-sm">{review.review_text}</p>
          </div>
        )}

        {review.status === "pending" && (
          <div className="flex gap-2">
            <Button type="button" size="sm" disabled={busy} onClick={() => onAccept(review.id)}>
              <CheckCircle2 className="mr-1 h-4 w-4" />
              {t("acceptReview")}
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={busy}
              onClick={() => onDecline(review.id)}
            >
              <XCircle className="mr-1 h-4 w-4" />
              {t("declineReview")}
            </Button>
          </div>
        )}

        {review.status === "accepted" && !showForm && (
          <Button type="button" size="sm" disabled={busy} onClick={() => setShowForm(true)}>
            <Send className="mr-1 h-4 w-4" />
            {t("submitReview")}
          </Button>
        )}

        {review.status === "accepted" && showForm && (
          <div className="space-y-2">
            <textarea
              value={reviewText}
              onChange={(event) => setReviewText(event.target.value)}
              placeholder={t("reviewPlaceholder")}
              className="w-full rounded-md border border-(--border) bg-(--background) p-2 text-sm"
              rows={4}
            />
            <div className="flex gap-2">
              <Button
                type="button"
                size="sm"
                disabled={busy || !reviewText.trim()}
                onClick={() => onComplete(review.id, reviewText)}
              >
                {t("submitReview")}
              </Button>
              <Button type="button" size="sm" variant="outline" onClick={() => setShowForm(false)}>
                {t("cancel")}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function CollaboratePage() {
  const t = useTranslations("collaborate");
  const tc = useTranslations("common");
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);

  const [activeTab, setActiveTab] = useState("directory");
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);
  const [flashMessage, setFlashMessage] = useState<string | null>(null);

  const isFaculty = user?.role === "faculty";

  const facultyQuery = useFacultyList(token);
  const incomingReviewsQuery = useIncomingReviews(token, isFaculty);
  const projectsQuery = useProjectsList(token);

  const requestReview = useRequestReview(token);
  const acceptReview = useAcceptReview(token);
  const declineReview = useDeclineReview(token);
  const completeReview = useCompleteReview(token);

  useEffect(() => {
    if (!flashMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => setFlashMessage(null), 2000);
    return () => window.clearTimeout(timeoutId);
  }, [flashMessage]);

  useEffect(() => {
    if (!selectedProjectId && projectsQuery.data?.length) {
      setSelectedProjectId(projectsQuery.data[0].id);
    }
  }, [projectsQuery.data, selectedProjectId]);

  const faculty = facultyQuery.data ?? [];
  const incomingReviews = incomingReviewsQuery.data ?? [];
  const projects = projectsQuery.data ?? [];

  const loading = token
    ? facultyQuery.isLoading || (!isFaculty && projectsQuery.isLoading) || (isFaculty && incomingReviewsQuery.isLoading)
    : false;

  const queryError =
    facultyQuery.error?.message ||
    projectsQuery.error?.message ||
    incomingReviewsQuery.error?.message ||
    null;

  const busy =
    requestReview.isPending ||
    acceptReview.isPending ||
    declineReview.isPending ||
    completeReview.isPending;

  const retryLoad = () => {
    setActionError(null);
    void facultyQuery.refetch();
    if (!isFaculty) {
      void projectsQuery.refetch();
    }
    if (isFaculty) {
      void incomingReviewsQuery.refetch();
    }
  };

  const handleRequestReview = async (facultyId: string) => {
    if (!token || !selectedProjectId) {
      setActionError(t("noProjectsForReview"));
      return;
    }

    try {
      setActionError(null);
      await requestReview.mutateAsync({ faculty_id: facultyId, project_id: selectedProjectId });
      setFlashMessage(t("reviewRequested"));
    } catch (error) {
      setActionError(error instanceof Error ? error.message : tc("retry"));
    }
  };

  const handleAccept = async (reviewId: string) => {
    if (!token) {
      return;
    }

    try {
      setActionError(null);
      await acceptReview.mutateAsync({ reviewId });
    } catch (error) {
      setActionError(error instanceof Error ? error.message : tc("retry"));
    }
  };

  const handleDecline = async (reviewId: string) => {
    if (!token) {
      return;
    }

    try {
      setActionError(null);
      await declineReview.mutateAsync({ reviewId });
    } catch (error) {
      setActionError(error instanceof Error ? error.message : tc("retry"));
    }
  };

  const handleComplete = async (reviewId: string, reviewText: string) => {
    if (!token) {
      return;
    }

    try {
      setActionError(null);
      await completeReview.mutateAsync({ reviewId, reviewText });
    } catch (error) {
      setActionError(error instanceof Error ? error.message : tc("retry"));
    }
  };

  const pendingCount = incomingReviews.filter((review) => review.status === "pending").length;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold">{t("title")}</h2>
              <p className="text-(--muted-foreground)">{t("subtitle")}</p>
            </div>
            {flashMessage && <Badge variant="success">{flashMessage}</Badge>}
          </div>

          {loading && (
            <div className="space-y-4">
              {[1, 2, 3].map((index) => (
                <Card key={index}>
                  <CardHeader>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-80" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}

          {queryError && (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-(--destructive)">{queryError}</p>
                <Button type="button" variant="outline" className="mt-4" onClick={retryLoad}>
                  {tc("retry")}
                </Button>
              </CardContent>
            </Card>
          )}

          {!loading && !queryError && (
            <div className="space-y-4">
              {actionError && (
                <Card>
                  <CardContent className="py-4">
                    <p className="text-sm text-(--destructive)">{actionError}</p>
                  </CardContent>
                </Card>
              )}

              <Tabs defaultValue="directory" value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                  <TabsTrigger value="directory">
                    <Users className="mr-1 h-4 w-4" />
                    {t("facultyDirectory")}
                  </TabsTrigger>
                  {isFaculty && (
                    <TabsTrigger value="reviews">
                      <MessageSquare className="mr-1 h-4 w-4" />
                      {t("incomingReviews")}
                      {pendingCount > 0 && (
                        <Badge className="ml-2 bg-amber-100 text-amber-800" variant="secondary">
                          {pendingCount}
                        </Badge>
                      )}
                    </TabsTrigger>
                  )}
                </TabsList>

                <TabsContent value="directory" className="mt-6 space-y-4">
                  {!isFaculty && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">{t("selectProject")}</CardTitle>
                        <CardDescription>{t("selectProjectDesc")}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        {projects.length === 0 ? (
                          <p className="text-sm text-(--muted-foreground)">{t("noProjectsForReview")}</p>
                        ) : (
                          <select
                            value={selectedProjectId}
                            aria-label={t("selectProject")}
                            title={t("selectProject")}
                            onChange={(event) => setSelectedProjectId(event.target.value)}
                            className="w-full rounded-md border border-(--border) bg-(--background) px-3 py-2 text-sm"
                          >
                            {projects.map((project) => (
                              <option key={project.id} value={project.id}>
                                {project.title}
                              </option>
                            ))}
                          </select>
                        )}
                      </CardContent>
                    </Card>
                  )}

                  {faculty.length === 0 ? (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <Users className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                        <p className="text-lg font-medium">{t("noFaculty")}</p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                      {faculty.map((facultyMember) => (
                        <FacultyCard
                          key={facultyMember.id}
                          faculty={facultyMember}
                          onRequestReview={handleRequestReview}
                          isStudent={!isFaculty}
                          canRequest={Boolean(selectedProjectId)}
                          isSubmitting={requestReview.isPending}
                        />
                      ))}
                    </div>
                  )}
                </TabsContent>

                {isFaculty && (
                  <TabsContent value="reviews" className="mt-6">
                    {incomingReviews.length === 0 ? (
                      <Card>
                        <CardContent className="py-12 text-center">
                          <MessageSquare className="mx-auto mb-4 h-12 w-12 text-(--muted-foreground)" />
                          <p className="text-lg font-medium">{t("noReviews")}</p>
                        </CardContent>
                      </Card>
                    ) : (
                      <div className="space-y-4">
                        {incomingReviews.map((review) => (
                          <ReviewCard
                            key={review.id}
                            review={review}
                            onAccept={handleAccept}
                            onDecline={handleDecline}
                            onComplete={handleComplete}
                            busy={busy}
                          />
                        ))}
                      </div>
                    )}
                  </TabsContent>
                )}
              </Tabs>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}